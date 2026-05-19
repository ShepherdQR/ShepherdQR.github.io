#!/usr/bin/env python3
"""Audit and preview migration from legacy HTML notes to Markdown.

The tool is intentionally non-destructive by default. It preserves date metadata
from legacy HTML comments and reports files that need manual review.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path


TYPE_VALUES = {"Books", "Thoughts", "Study", "Videos"}


@dataclass
class IndexEntry:
    date: str
    href: str
    text: str


@dataclass
class MigrationRecord:
    path: Path
    rel_path: str
    content_type: str
    content_id: str
    title: str
    created: str | None
    created_date: str | None
    updated: str | None
    updated_date: str | None
    published: str | None
    published_source: str
    status: str
    created_source: str
    updated_source: str
    complexity: int
    review_reasons: list[str]
    markdown: str

    @property
    def can_migrate(self) -> bool:
        return not self.review_reasons


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def normalize_rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def parse_index_data(root: Path) -> dict[tuple[str, str], IndexEntry]:
    index_path = root / "index-data.js"
    if not index_path.exists():
        return {}

    text = read_text(index_path)
    entries: dict[tuple[str, str], IndexEntry] = {}
    pattern = re.compile(
        r"\{\s*date:\s*'(?P<date>[^']+)'\s*,\s*href:\s*'(?P<href>(?:\\'|[^'])*)'\s*,\s*text:\s*(?:'(?P<text1>(?:\\'|[^'])*)'|\"(?P<text2>(?:\\\"|[^\"])*)\")",
        re.S,
    )

    for match in pattern.finditer(text):
        href = match.group("href").replace("\\'", "'")
        item_text = (match.group("text1") or match.group("text2") or "").replace("\\'", "'").replace('\\"', '"')
        candidates = [href, item_text]
        for candidate in candidates:
            parsed = parse_type_id_title(candidate)
            if parsed:
                content_type, content_id, _ = parsed
                entries[(content_type, content_id)] = IndexEntry(
                    date=match.group("date"),
                    href=href,
                    text=item_text,
                )
    return entries


def parse_type_id_title(value: str) -> tuple[str, str, str] | None:
    basename = value.split("?md=")[-1].split("/")[-1]
    basename = re.sub(r"\.(html|md)$", "", basename, flags=re.I)
    basename = html.unescape(basename)

    match = re.match(r"^\[(?P<type>[^\]]+)\]\[(?P<id>\d{4})\](?P<rest>.+)?$", basename)
    if not match:
        return None

    content_type = match.group("type")
    content_id = match.group("id")
    rest = (match.group("rest") or "").strip()

    if rest.startswith("[[") and rest.endswith("]"):
        title = rest[1:-1].strip()
    elif rest.startswith("[") and rest.endswith("]") and "][" not in rest[1:-1]:
        title = rest[1:-1].strip()
    else:
        title = rest.strip()

    if content_type not in TYPE_VALUES:
        return None

    return content_type, content_id, title or f"{content_type}-{content_id}"


def extract_comment_field(text: str, names: tuple[str, ...]) -> str | None:
    head = text[:2000]
    for name in names:
        pattern = re.compile(rf"[@\s*-]*{re.escape(name)}\s*:\s*(?P<value>[0-9]{{4}}[-/][0-9]{{1,2}}[-/][0-9]{{1,2}}(?:\s+[0-9]{{1,2}}:[0-9]{{1,2}}(?::[0-9]{{1,2}})?)?)")
        match = pattern.search(head)
        if match:
            return normalize_datetime(match.group("value"))
    return None


def normalize_datetime(value: str) -> str:
    value = value.strip().replace("/", "-")
    return re.sub(r"\s+", " ", value)


def date_part(value: str | None) -> str | None:
    if not value:
        return None
    match = re.match(r"^(\d{4}-\d{1,2}-\d{1,2})", value)
    if not match:
        return None
    parts = match.group(1).split("-")
    try:
        date_value = dt.date(int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        return None
    return date_value.isoformat()


def slugify(title: str, content_type: str, content_id: str) -> str:
    normalized = unicodedata.normalize("NFKD", title)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    if len(slug) < 4 or slug.isdigit():
        return f"{content_type.lower()}-{content_id}"
    return slug


def complexity_level(text: str) -> tuple[int, list[str]]:
    body = extract_inner_html(text)
    lower = body.lower()
    reasons: list[str] = []
    level = 1

    if "writestring" in lower or "<ol" in lower or "<li" in lower or "<blockquote" in lower or "<pre" in lower:
        level = max(level, 2)
    if "<img" in lower or "<table" in lower or "$$" in body or "\\(" in body or "\\[" in body:
        level = max(level, 3)
        reasons.append("rich content requires review")
    if "d3" in lower or "<canvas" in lower or "<iframe" in lower:
        level = max(level, 4)
        reasons.append("complex interactive HTML")

    return level, reasons


def extract_inner_html(text: str) -> str:
    marker_match = re.search(r'<div\s+class=["\']inner["\'][^>]*>(?P<body>[\s\S]*?)<!--We donnot modify lines after this-->', text, re.I)
    if marker_match:
        return marker_match.group("body")

    div_match = re.search(r'<div\s+class=["\']inner["\'][^>]*>(?P<body>[\s\S]*?)</div>\s*</body>', text, re.I)
    if div_match:
        return div_match.group("body")

    body_match = re.search(r"<body[^>]*>(?P<body>[\s\S]*?)</body>", text, re.I)
    if body_match:
        return body_match.group("body")

    return text


def replace_script_strings(fragment: str) -> str:
    def decode_js_string(content: str, quote: str) -> str:
        if quote == "`":
            return content.replace("\\`", "`")
        replacements = {
            "\\n": "\n",
            "\\r": "\r",
            "\\t": "\t",
            "\\'": "'",
            '\\"': '"',
            "\\\\": "\\",
        }
        for source, target in replacements.items():
            content = content.replace(source, target)
        return content

    def replace_match(match: re.Match[str]) -> str:
        content = decode_js_string(match.group("content"), match.group("quote")).strip("\n")
        if match.group("writer").lower() == "writeitem":
            return replace_write_item(content)
        return "\n\n" + content + "\n\n"

    def replace_write_item(content: str) -> str:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        return "\n" + "\n".join(f"- {line}" for line in lines) + "\n"

    string_script = re.compile(
        r"<script[^>]*>\s*var\s+string\s*=\s*(?P<quote>`|'|\")(?P<content>[\s\S]*?)(?P=quote)\s*;\s*(?P<writer>writeString|writeItem)\(string\)\s*;?\s*</script>",
        re.I,
    )
    return string_script.sub(replace_match, fragment)


def preserve_or_strip_script(match: re.Match[str]) -> str:
    script = match.group(0)
    lower = script.lower()
    boilerplate_markers = (
        "retrieveTitle".lower(),
        "currentInnerTitle".lower(),
        "supportMobile".lower(),
        "styleHeader".lower(),
        "googleanalyticsobject".lower(),
        "ga('create'",
    )
    if any(marker in lower for marker in boilerplate_markers):
        return "\n"
    return "\n\n" + script.strip() + "\n\n"


def stash_raw_blocks(fragment: str) -> tuple[str, list[str]]:
    blocks: list[str] = []

    def stash(match: re.Match[str]) -> str:
        token = f"@@RAW_HTML_BLOCK_{len(blocks)}@@"
        blocks.append(match.group(0).strip())
        return "\n\n" + token + "\n\n"

    for tag in ("script", "svg", "table"):
        fragment = re.sub(rf"<{tag}\b[\s\S]*?</{tag}>", stash, fragment, flags=re.I)
    return fragment, blocks


def restore_raw_blocks(markdown: str, blocks: list[str]) -> str:
    for index, block in enumerate(blocks):
        markdown = markdown.replace(f"@@RAW_HTML_BLOCK_{index}@@", block)
    return markdown


def html_to_markdown(fragment: str) -> str:
    fragment = replace_script_strings(fragment)
    fragment = re.sub(r"<script[\s\S]*?</script>", preserve_or_strip_script, fragment, flags=re.I)
    fragment = re.sub(r"<h[12][^>]*>[\s\S]*?</h[12]>", "\n", fragment, flags=re.I)

    fragment = re.sub(
        r'<a\s+[^>]*href\s*=\s*["\'](?P<href>[^"\']+)["\'][^>]*>(?P<label>[\s\S]*?)</a>',
        lambda m: f"[{strip_tags(m.group('label')).strip()}]({m.group('href').strip()})",
        fragment,
        flags=re.I,
    )
    fragment = re.sub(
        r'<img\s+[^>]*src\s*=\s*["\'](?P<src>[^"\']+)["\'][^>]*>',
        lambda m: f"\n\n![]({m.group('src').strip()})\n\n",
        fragment,
        flags=re.I,
    )
    fragment = re.sub(r"<br\s*/?>", "\n", fragment, flags=re.I)
    fragment = re.sub(r"<hr\s*/?>", "\n\n---\n\n", fragment, flags=re.I)
    fragment = re.sub(r"</p\s*>", "\n\n", fragment, flags=re.I)
    fragment = re.sub(r"<p(?:\s[^>]*)?>", "\n\n", fragment, flags=re.I)
    fragment = re.sub(
        r"<li[^>]*>(?P<item>[\s\S]*?)</li>",
        lambda m: "\n- " + single_line(strip_tags(m.group("item"))),
        fragment,
        flags=re.I,
    )
    fragment = re.sub(r"</?(ol|ul)[^>]*>", "\n", fragment, flags=re.I)
    fragment, raw_blocks = stash_raw_blocks(fragment)
    fragment = strip_tags(fragment)
    fragment = html.unescape(fragment)
    fragment = normalize_markdown(fragment)
    return restore_raw_blocks(fragment, raw_blocks)


def strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value)


def single_line(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def normalize_markdown(value: str) -> str:
    lines = [line.rstrip() for line in value.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    cleaned: list[str] = []
    blank_count = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            blank_count += 1
            if blank_count <= 2:
                cleaned.append("")
            continue
        blank_count = 0
        cleaned.append(stripped if line.startswith(" ") and not stripped.startswith("- ") else line.strip())

    return "\n".join(cleaned).strip() + "\n"


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_front_matter(record: MigrationRecord) -> str:
    slug = slugify(record.title, record.content_type, record.content_id)
    lines = [
        "---",
        f"type: {record.content_type}",
        f"id: {yaml_quote(record.content_id)}",
        f"title: {yaml_quote(record.title)}",
        f"created: {yaml_quote(record.created or '')}",
        f"created_date: {yaml_quote(record.created_date or '')}",
        f"published: {yaml_quote(record.published or '')}",
        f"updated: {yaml_quote(record.updated or '')}",
        f"updated_date: {yaml_quote(record.updated_date or '')}",
        f"slug: {yaml_quote(slug)}",
        f"status: {yaml_quote(record.status)}",
        "source:",
        f"  legacy_path: {yaml_quote(record.rel_path)}",
        "  date_source:",
        f"    created: {yaml_quote(record.created_source)}",
        f"    published: {yaml_quote(record.published_source)}",
        f"    updated: {yaml_quote(record.updated_source)}",
        "migration:",
        '  status: "draft"',
        f"  complexity: {record.complexity}",
        "---",
        "",
    ]
    return "\n".join(lines)


def analyze_file(path: Path, root: Path, index_entries: dict[tuple[str, str], IndexEntry]) -> MigrationRecord:
    text = read_text(path)
    rel_path = normalize_rel(path, root)
    parsed = parse_type_id_title(path.name)
    if parsed:
        content_type, content_id, title = parsed
    else:
        content_type, content_id, title = "Unknown", "0000", path.stem

    created = extract_comment_field(text, ("@Date", "Date"))
    updated = extract_comment_field(text, ("@LastEditTime", "LastEditTime"))
    created_date = date_part(created)
    updated_date = date_part(updated)

    published_entry = index_entries.get((content_type, content_id))
    if published_entry:
        published = published_entry.date
        published_source = "index-data"
        status = "published"
    else:
        published = created_date
        published_source = "created-date-fallback"
        status = "draft"

    created_source = "html-comment"
    updated_source = "html-comment"
    if not created and published_entry:
        created = published_entry.date
        created_date = published_entry.date
        created_source = "index-data-fallback-missing-html-comment"
    if not updated and published_entry:
        updated = published_entry.date
        updated_date = published_entry.date
        updated_source = "index-data-fallback-missing-html-comment"

    complexity, complexity_reasons = complexity_level(text)
    review_reasons = list(complexity_reasons)

    if not parsed:
        review_reasons.append("filename does not contain supported type/id")
    if created_source != "html-comment":
        review_reasons.append("created date falls back to index-data")
    if updated_source != "html-comment":
        review_reasons.append("updated date falls back to index-data")
    if not created or not created_date:
        review_reasons.append("missing created date")
    if not updated or not updated_date:
        review_reasons.append("missing updated date")
    if not published:
        review_reasons.append("missing published date")
    if complexity >= 4:
        review_reasons.append("defer interactive page")

    body = extract_inner_html(text)
    body_md = html_to_markdown(body)
    front_matter_placeholder = MigrationRecord(
        path=path,
        rel_path=rel_path,
        content_type=content_type,
        content_id=content_id,
        title=title,
        created=created,
        created_date=created_date,
        updated=updated,
        updated_date=updated_date,
        published=published,
        published_source=published_source,
        status=status,
        created_source=created_source,
        updated_source=updated_source,
        complexity=complexity,
        review_reasons=review_reasons,
        markdown="",
    )
    markdown = build_front_matter(front_matter_placeholder) + f"# {title}\n\n" + body_md
    front_matter_placeholder.markdown = markdown
    return front_matter_placeholder


def find_html_files(root: Path) -> list[Path]:
    return sorted((root / "qrthoughts").rglob("*.html"))


def write_preview(record: MigrationRecord, root: Path, output_dir: Path, overwrite: bool, skip_existing: bool) -> tuple[Path, bool]:
    target = output_dir / record.path.relative_to(root)
    target = target.with_suffix(".md")
    if target.exists() and skip_existing:
        return target, False
    if target.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(record.markdown, encoding="utf-8", newline="\n")
    return target, True


def write_in_place(record: MigrationRecord, overwrite: bool, skip_existing: bool) -> tuple[Path, bool]:
    target = record.path.with_suffix(".md")
    if target.exists() and skip_existing:
        return target, False
    if target.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite {target}")
    target.write_text(record.markdown, encoding="utf-8", newline="\n")
    return target, True


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--path", action="append", help="Specific legacy HTML path to audit. Can be repeated.")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of files processed.")
    parser.add_argument("--sample", type=int, default=10, help="Number of sample records to print.")
    parser.add_argument("--write-preview", help="Write Markdown previews under this output directory.")
    parser.add_argument("--in-place", action="store_true", help="Create .md files next to legacy .html files.")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting generated .md files.")
    parser.add_argument("--skip-existing", action="store_true", help="Skip generated .md files that already exist.")
    parser.add_argument("--include-review", action="store_true", help="Write preview files even when manual review is required.")
    parser.add_argument("--published-only", action="store_true", help="Write only files that have an index-data publication entry.")
    return parser


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    args = build_arg_parser().parse_args(argv)
    root = Path(args.root).resolve()
    index_entries = parse_index_data(root)

    if args.path:
        files = [Path(item) if Path(item).is_absolute() else root / item for item in args.path]
    else:
        files = find_html_files(root)

    if args.limit > 0:
        files = files[: args.limit]

    records = [analyze_file(path, root, index_entries) for path in files]
    total = len(records)
    ready = sum(1 for record in records if record.can_migrate)
    review = total - ready

    levels = {level: 0 for level in range(1, 5)}
    for record in records:
        levels[record.complexity] = levels.get(record.complexity, 0) + 1

    print(f"Legacy HTML files audited: {total}")
    print(f"Ready without review: {ready}")
    print(f"Needs review/defer: {review}")
    print("Complexity levels: " + ", ".join(f"L{level}={levels.get(level, 0)}" for level in range(1, 5)))
    print()

    for record in records[: args.sample]:
        status = "ready" if record.can_migrate else "review"
        reasons = "; ".join(record.review_reasons) if record.review_reasons else "-"
        print(f"[{status}] {record.rel_path}")
        print(f"  type/id/title: {record.content_type}/{record.content_id}/{record.title}")
        print(f"  dates: created={record.created or '-'} published={record.published or '-'} updated={record.updated or '-'}")
        print(f"  complexity: L{record.complexity}; reasons: {reasons}")

    if args.write_preview:
        output_dir = Path(args.write_preview)
        if not output_dir.is_absolute():
            output_dir = root / output_dir
        written = 0
        skipped = 0
        for record in records:
            if args.published_only and record.status != "published":
                continue
            if record.can_migrate or args.include_review:
                _, did_write = write_preview(record, root, output_dir, args.overwrite, args.skip_existing)
                written += 1 if did_write else 0
                skipped += 0 if did_write else 1
        print()
        print(f"Preview Markdown files written: {written} -> {output_dir}")
        if skipped:
            print(f"Preview Markdown files skipped because they already exist: {skipped}")

    if args.in_place:
        written = 0
        skipped = 0
        for record in records:
            if args.published_only and record.status != "published":
                continue
            if record.can_migrate or args.include_review:
                _, did_write = write_in_place(record, args.overwrite, args.skip_existing)
                written += 1 if did_write else 0
                skipped += 0 if did_write else 1
        print()
        print(f"In-place Markdown files written: {written}")
        if skipped:
            print(f"In-place Markdown files skipped because they already exist: {skipped}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
