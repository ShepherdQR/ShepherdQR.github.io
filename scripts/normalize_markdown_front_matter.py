#!/usr/bin/env python3
"""Add required front matter to existing Markdown notes.

The script preserves the original body and date comments. It only targets
content notes under qrthoughts and skips README files.
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
LEADING_COMMENTS_RE = re.compile(r"^\ufeff?(?:<!--[\s\S]*?-->\s*)*")
FRONT_MATTER_RE = re.compile(r"^---\s*\n")


@dataclass
class IndexEntry:
    date: str
    href: str
    text: str


@dataclass
class MarkdownNote:
    path: Path
    rel_path: str
    content_type: str
    content_id: str
    title: str
    created: str
    created_date: str
    published: str
    updated: str
    updated_date: str
    slug: str
    date_sources: dict[str, str]
    body: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def normalize_rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def has_front_matter(text: str) -> bool:
    _, body = split_leading_comments(text)
    return bool(FRONT_MATTER_RE.match(body))


def split_leading_comments(text: str) -> tuple[str, str]:
    match = LEADING_COMMENTS_RE.match(text)
    if not match:
        return "", text
    return text[: match.end()], text[match.end():]


def insert_front_matter_after_leading_comments(note: MarkdownNote) -> str:
    comments, body = split_leading_comments(note.body)
    return comments + build_front_matter(note) + body.lstrip()


def parse_index_data(root: Path) -> dict[tuple[str, str], IndexEntry]:
    index_path = root / "index-data.js"
    if not index_path.exists():
        return {}

    text = read_text(index_path)
    entries: dict[tuple[str, str], IndexEntry] = {}
    pattern = re.compile(
        r"\{\s*date:\s*'(?P<date>[^']+)'\s*,\s*href:\s*'(?P<href>(?:\\'|[^'])*)'\s*,\s*text:\s*'(?P<text>(?:\\'|[^'])*)'",
        re.S,
    )

    for match in pattern.finditer(text):
        href = match.group("href").replace("\\'", "'")
        item_text = match.group("text").replace("\\'", "'")
        for candidate in (href, item_text):
            parsed = parse_type_id_title(candidate)
            if parsed:
                content_type, content_id, _ = parsed
                entries[(content_type, content_id)] = IndexEntry(match.group("date"), href, item_text)
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
    head = text[:2400]
    for name in names:
        pattern = re.compile(
            rf"[@\s*\-]*{re.escape(name)}\s*:\s*(?P<value>[0-9]{{4}}[-/][0-9]{{1,2}}[-/][0-9]{{1,2}}(?:\s+[0-9]{{1,2}}:[0-9]{{1,2}}(?::[0-9]{{1,2}})?)?)"
        )
        match = pattern.search(head)
        if match:
            return normalize_datetime(match.group("value"))
    return None


def normalize_datetime(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().replace("/", "-"))


def date_part(value: str | None) -> str | None:
    if not value:
        return None
    match = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})", value)
    if not match:
        return None
    try:
        parsed = dt.date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None
    return parsed.isoformat()


def extract_title(text: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+?)\s*$", text, flags=re.M)
    if not match:
        return fallback
    return match.group(1).strip()


def slugify(title: str, content_type: str, content_id: str) -> str:
    normalized = unicodedata.normalize("NFKD", title)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    if len(slug) < 4 or slug.isdigit():
        return f"{content_type.lower()}-{content_id}"
    return slug


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_front_matter(note: MarkdownNote) -> str:
    return "\n".join(
        [
            "---",
            f"type: {note.content_type}",
            f"id: {yaml_quote(note.content_id)}",
            f"title: {yaml_quote(note.title)}",
            f"created: {yaml_quote(note.created)}",
            f"created_date: {yaml_quote(note.created_date)}",
            f"published: {yaml_quote(note.published)}",
            f"updated: {yaml_quote(note.updated)}",
            f"updated_date: {yaml_quote(note.updated_date)}",
            f"slug: {yaml_quote(note.slug)}",
            'status: "published"',
            "source:",
            f"  path: {yaml_quote(note.rel_path)}",
            "  date_source:",
            f"    created: {yaml_quote(note.date_sources['created'])}",
            f"    published: {yaml_quote(note.date_sources['published'])}",
            f"    updated: {yaml_quote(note.date_sources['updated'])}",
            "---",
            "",
        ]
    )


def derive_note(path: Path, root: Path, index_entries: dict[tuple[str, str], IndexEntry]) -> MarkdownNote | None:
    if path.name.lower() == "readme.md":
        return None

    text = read_text(path)
    if has_front_matter(text):
        return None

    parsed = parse_type_id_title(path.name)
    if not parsed:
        return None

    content_type, content_id, filename_title = parsed
    sibling_html = path.with_suffix(".html")
    sibling_text = read_text(sibling_html) if sibling_html.exists() else ""

    index_entry = index_entries.get((content_type, content_id))

    created = extract_comment_field(text, ("@Date", "Date"))
    created_source = "markdown-comment"

    updated = extract_comment_field(text, ("@LastEditTime", "LastEditTime"))
    updated_source = "markdown-comment"
    if not updated and sibling_text:
        updated = extract_comment_field(sibling_text, ("@LastEditTime", "LastEditTime"))
        updated_source = "sibling-html-comment"

    if index_entry:
        published = index_entry.date
        published_source = "index-data"
    else:
        published = date_part(created) or ""
        published_source = "created-date-fallback"

    if not created:
        created = published
        created_source = "published-fallback"
    if not updated:
        updated = created
        updated_source = "created-fallback"

    created_date = date_part(created) or published
    updated_date = date_part(updated) or created_date
    title = filename_title

    return MarkdownNote(
        path=path,
        rel_path=normalize_rel(path, root),
        content_type=content_type,
        content_id=content_id,
        title=title,
        created=created,
        created_date=created_date,
        published=published,
        updated=updated,
        updated_date=updated_date,
        slug=slugify(title, content_type, content_id),
        date_sources={"created": created_source, "published": published_source, "updated": updated_source},
        body=text,
    )


def find_markdown_notes(root: Path) -> list[Path]:
    return sorted((root / "qrthoughts").rglob("*.md"))


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--write", action="store_true", help="Write front matter into Markdown files.")
    return parser


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = build_arg_parser().parse_args(argv)
    root = Path(args.root).resolve()
    index_entries = parse_index_data(root)

    notes = [note for path in find_markdown_notes(root) if (note := derive_note(path, root, index_entries))]

    print(f"Markdown notes needing front matter: {len(notes)}")
    for note in notes:
        print(
            f"{note.rel_path}: created={note.created} published={note.published} updated={note.updated} title={note.title}"
        )

    if args.write:
        for note in notes:
            write_text(note.path, insert_front_matter_after_leading_comments(note))
        print(f"Updated Markdown files: {len(notes)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
