#!/usr/bin/env python3
"""Generate homepage data from Markdown front matter.

Markdown is the canonical content source. The legacy index can still be merged
explicitly for diagnostics or transition work, but it is not used by default.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote


FIELD_RE = re.compile(r"^(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?P<value>.*)$")
FRONT_MATTER_RE = re.compile(
    r"^\ufeff?(?:<!--[\s\S]*?-->\s*)*---\s*\n(?P<yaml>[\s\S]*?)\n---\s*\n"
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
INDEX_ITEM_RE = re.compile(
    r"\{\s*date:\s*'(?P<date>[^']+)'\s*,\s*href:\s*'(?P<href>(?:\\'|[^'])*)'\s*,\s*text:\s*(?:'(?P<text1>(?:\\'|[^'])*)'|\"(?P<text2>(?:\\\"|[^\"])*)\")",
    re.S,
)
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\((?P<target><[^>]+>|[^\s)]+)")
TRUE_VALUES = {"1", "true", "yes", "on"}
MAPPING_SOURCES = {"frontmatter", "selected", "taxonomy", "collection_default", "unmapped"}
COLLECTION_DEFAULT_FIELD_IDS = {
    "Books": ["VL-READING-LITERATURE-POETRY"],
}
REVISION_LIST_FIELDS = {
    "supersedes": "supersedes",
    "superseded_by": "supersededBy",
    "errata": "errata",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return value


def parse_list(value: str) -> list[str]:
    value = (value or "").strip()
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, list):
        return [str(item).strip() for item in parsed if str(item).strip()]
    return [item.strip() for item in value.strip("[]").split(",") if item.strip()]


def parse_bool(value: str) -> bool:
    return (value or "").strip().lower() in TRUE_VALUES


def markdown_body(text: str) -> str:
    match = FRONT_MATTER_RE.match(text)
    return text[match.end() :] if match else text


def markdown_excerpt(body: str, limit: int = 180) -> str:
    """Return the first prose paragraph, not a flattened Markdown document.

    Homepage summaries are a public projection. Treat headings, code, lists,
    tables, media, link definitions and bare URLs as structure rather than
    prose so absent front-matter summaries do not leak syntax into cards.
    """

    cleaned_body = re.sub(r"<!--[\s\S]*?-->", "\n", body)
    cleaned_body = re.sub(r"<script\b[\s\S]*?</script>", "\n", cleaned_body, flags=re.I)
    cleaned_body = re.sub(r"<style\b[\s\S]*?</style>", "\n", cleaned_body, flags=re.I)
    lines = cleaned_body.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    paragraphs: list[list[str]] = []
    paragraph: list[str] = []
    in_fence = False
    fence_marker = ""

    def flush() -> None:
        nonlocal paragraph
        if paragraph:
            paragraphs.append(paragraph)
            paragraph = []

    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        fence = re.match(r"^\s{0,3}(`{3,}|~{3,})", raw_line)
        if fence:
            marker = fence.group(1)[0]
            if not in_fence:
                flush()
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            continue
        if in_fence:
            continue
        if not stripped:
            flush()
            continue

        next_line = lines[index + 1].strip() if index + 1 < len(lines) else ""
        is_setext_title = bool(next_line and re.fullmatch(r"(?:=+|-+)", next_line))
        is_structure = any(
            (
                re.match(r"^\s{0,3}#{1,6}(?:\s+|$)", raw_line),
                re.fullmatch(r"\s*(?:={3,}|-{3,}|\*{3,}|_{3,})\s*", raw_line),
                re.match(r"^\s*(?:[-+*]|\d+[.)])\s+", raw_line),
                re.match(r"^\s*>", raw_line),
                re.match(r"^\s*\[[^\]]+\]:\s*\S+", raw_line),
                re.match(r"^\s*!\[[^\]]*\]\([^)]*\)\s*$", raw_line),
                re.match(r"^\s*</?[A-Za-z][^>]*>\s*$", raw_line),
                re.fullmatch(r"\s*<https?://[^>]+>\s*", raw_line, flags=re.I),
                re.fullmatch(r"\s*https?://\S+\s*", raw_line, flags=re.I),
                re.fullmatch(r"\s*\|?(?:\s*:?-+:?\s*\|)+\s*", raw_line),
                re.fullmatch(r"\s*\|.*\|\s*", raw_line),
                is_setext_title,
            )
        )
        if is_structure:
            flush()
            continue
        if "|" in stripped and next_line and re.search(r"\|\s*:?-{3,}:?", next_line):
            flush()
            continue
        paragraph.append(stripped)
    flush()

    for candidate_lines in paragraphs:
        text = " ".join(candidate_lines)
        text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
        text = re.sub(r"<https?://[^>]+>", " ", text, flags=re.I)
        text = re.sub(r"(?<![\w/])https?://\S+", " ", text, flags=re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\[(?:\^)?[^\]]+\]", " ", text)
        text = re.sub(r"[`*_~|]", "", text)
        text = re.sub(r"\\([#>*_`~\\])", r"\1", text)
        text = re.sub(r"\s+", " ", text).strip()
        if not text or not re.search(r"[\w\u3400-\u9fff]", text):
            continue
        if len(text) <= limit:
            return text
        return text[:limit].rstrip(" ，。；：、,.!！?？)") + "…"
    return ""


def detects_math(body: str) -> bool:
    patterns = [
        r"\$\$[\s\S]+?\$\$",
        r"(?<!\\)\$(?![\s${])[^$\n]{1,300}(?<!\\)\$",
        r"\\\([\s\S]+?\\\)",
        r"\\\[[\s\S]+?\\\]",
        r"\\begin\{",
    ]
    return any(re.search(pattern, body) for pattern in patterns)


def detects_interactive(body: str) -> bool:
    return bool(re.search(r"<script\b|\bd3\.", body, flags=re.I))


def normalize_lead_image(value: str, source_path: Path, root: Path) -> str:
    value = (value or "").strip().strip("<>")
    if not value:
        return ""
    if re.match(r"^[a-z][a-z0-9+.-]*:", value, flags=re.I) or value.startswith("//"):
        return value
    if value.startswith("/"):
        return value
    try:
        resolved = (source_path.parent / value).resolve()
        return "/" + resolved.relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return value


def first_markdown_image(body: str, source_path: Path, root: Path) -> str:
    match = MARKDOWN_IMAGE_RE.search(body)
    if not match:
        return ""
    return normalize_lead_image(match.group("target"), source_path, root)


def date_part(value: str) -> str:
    value = (value or "").strip()
    if DATETIME_RE.fullmatch(value):
        return value[:10]
    if DATE_RE.fullmatch(value):
        return value
    return ""


def normalize_sort_datetime(value: str, expected_date: str) -> str:
    value = (value or "").strip()
    if not expected_date or date_part(value) != expected_date:
        return ""
    if DATETIME_RE.fullmatch(value):
        return value.replace(" ", "T")
    if DATE_RE.fullmatch(value):
        return value + "T00:00:00"
    return ""


def item_sort_key(item: dict[str, str]) -> tuple[str, str, str, str, str]:
    published_date = date_part(item.get("published", ""))
    return (
        published_date,
        normalize_sort_datetime(item.get("created", ""), published_date),
        normalize_sort_datetime(item.get("updated", ""), published_date),
        item.get("type", ""),
        item.get("id", ""),
    )


def parse_type_id_title(value: str) -> tuple[str, str, str] | None:
    basename = value.split("?md=")[-1].split("/")[-1]
    basename = re.sub(r"\.(html|md)$", "", basename, flags=re.I)
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
    return content_type, content_id, title or f"{content_type}-{content_id}"


def parse_front_matter(text: str) -> dict[str, str] | None:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return None

    data: dict[str, str] = {}
    for line in match.group("yaml").splitlines():
        if line.startswith(" ") or not line.strip():
            continue
        field = FIELD_RE.match(line)
        if field:
            data[field.group("key")] = parse_scalar(field.group("value"))
    return data


def load_narrative_contract(root: Path) -> dict[str, object]:
    """Load the declared public narrative taxonomy used by item projections."""

    source_path = root / "data" / "site-plane.json"
    try:
        plane = json.loads(read_text(source_path))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot load narrative contract from {source_path}: {exc}") from exc

    lines = ((plane.get("narrative_lines") or {}).get("items") or [])
    if not isinstance(lines, list) or not lines:
        raise ValueError(f"Narrative contract has no lines: {source_path}")

    order: list[str] = []
    aliases: dict[str, str] = {}
    series: dict[str, list[str]] = {}
    tags: dict[str, list[str]] = {}
    for line in lines:
        if not isinstance(line, dict) or not line.get("id"):
            raise ValueError(f"Narrative contract contains a line without id: {source_path}")
        field_id = str(line["id"]).strip()
        if field_id in order:
            raise ValueError(f"Narrative contract contains duplicate id {field_id}: {source_path}")
        order.append(field_id)
        for alias in (field_id, line.get("title_zh"), line.get("title_en"), line.get("title")):
            if alias:
                alias_key = str(alias).strip().casefold()
                existing = aliases.get(alias_key)
                if existing and existing != field_id:
                    raise ValueError(
                        f"Narrative alias {alias!s} maps to both {existing} and {field_id}: {source_path}"
                    )
                aliases[alias_key] = field_id
        for series_name in line.get("series_filters") or []:
            series.setdefault(str(series_name).strip().casefold(), []).append(field_id)
        for tag in line.get("tags") or []:
            tags.setdefault(str(tag).strip().casefold(), []).append(field_id)

    selected: dict[tuple[str, str], list[str]] = {}
    selected_entries = ((plane.get("selected_entries") or {}).get("items") or [])
    for entry in selected_entries:
        if not isinstance(entry, dict):
            continue
        key = (str(entry.get("type", "")), str(entry.get("id", "")))
        field_value = str(entry.get("field_id") or entry.get("field") or "").strip()
        field_id = aliases.get(field_value.casefold())
        if all(key) and field_id:
            selected.setdefault(key, []).append(field_id)
        elif all(key) and field_value:
            raise ValueError(
                f"Selected entry {key[0]} {key[1]} references unknown narrative field: {field_value}"
            )

    for content_type, defaults in COLLECTION_DEFAULT_FIELD_IDS.items():
        missing = [field_id for field_id in defaults if field_id not in order]
        if missing:
            raise ValueError(
                f"Collection default for {content_type} references unknown narrative id(s): "
                + ", ".join(missing)
            )

    return {
        "order": order,
        "aliases": aliases,
        "series": series,
        "tags": tags,
        "selected": selected,
    }


def ordered_field_ids(field_ids: list[str], contract: dict[str, object]) -> list[str]:
    order = list(contract.get("order") or [])
    unique = set(field_ids)
    return [field_id for field_id in order if field_id in unique]


def resolve_narrative_mapping(
    data: dict[str, str],
    contract: dict[str, object],
    source_path: str,
) -> tuple[list[str], str]:
    """Resolve a transparent narrative mapping with an explicit provenance."""

    aliases = dict(contract.get("aliases") or {})
    explicit_ids = parse_list(data.get("field_ids", "") or data.get("fieldIds", ""))
    narrative_values = parse_list(data.get("narrative", ""))
    if explicit_ids or narrative_values:
        resolved: list[str] = []
        unknown: list[str] = []
        for value in explicit_ids:
            if value in (contract.get("order") or []):
                resolved.append(value)
            else:
                unknown.append(value)
        for value in narrative_values:
            field_id = aliases.get(value.strip().casefold())
            if field_id:
                resolved.append(str(field_id))
            else:
                unknown.append(value)
        if unknown:
            raise ValueError(
                f"Unknown narrative mapping in {source_path}: {', '.join(unknown)}"
            )
        return ordered_field_ids(resolved, contract), "frontmatter"

    key = (data.get("type", ""), data.get("id", ""))
    selected = dict(contract.get("selected") or {}).get(key) or []
    if selected:
        return ordered_field_ids(list(selected), contract), "selected"

    resolved = []
    series_name = data.get("series", "").strip().casefold()
    if series_name:
        resolved.extend(dict(contract.get("series") or {}).get(series_name) or [])
    for tag in parse_list(data.get("tags", "")):
        resolved.extend(dict(contract.get("tags") or {}).get(tag.casefold()) or [])
    if resolved:
        return ordered_field_ids(resolved, contract), "taxonomy"

    defaults = COLLECTION_DEFAULT_FIELD_IDS.get(data.get("type", ""), [])
    if defaults:
        return ordered_field_ids(defaults, contract), "collection_default"
    return [], "unmapped"


def project_revision_fields(item: dict[str, object], data: dict[str, str]) -> None:
    revision = data.get("revision", "").strip()
    revision_status = data.get("revision_status", "").strip()
    if revision:
        item["revision"] = revision
    if revision_status:
        item["revisionStatus"] = revision_status
    for source_field, output_field in REVISION_LIST_FIELDS.items():
        values = parse_list(data.get(source_field, ""))
        if values:
            item[output_field] = values


def render_href(path: Path, root: Path) -> str:
    rel = path.relative_to(root).as_posix()
    return f"render.html?md={quote('/' + rel[:-3], safe='/')}"


def clean_article_href(content_type: str, content_id: str) -> str:
    return f"/{content_type.lower()}/{content_id}/"


def normalize_legacy_href(href: str, root: Path) -> str:
    if href.startswith("render.html?"):
        return href
    if href.startswith("http://") or href.startswith("https://"):
        return href

    probe = href
    if probe.startswith("./"):
        probe = probe[2:]
    if Path(probe).suffix:
        return href

    html_path = root / (probe + ".html")
    if html_path.exists():
        return href + ".html"
    return href


def parse_legacy_index_items(root: Path) -> list[dict[str, str]]:
    index_path = root / "index-data.js"
    if not index_path.exists():
        return []

    text = read_text(index_path)
    items: list[dict[str, str]] = []
    used_keys: set[tuple[str, str]] = set()

    for match in INDEX_ITEM_RE.finditer(text):
        date = match.group("date")
        href = match.group("href").replace("\\'", "'")
        label_text = (match.group("text1") or match.group("text2") or "").replace("\\'", "'").replace('\\"', '"')
        parsed = parse_type_id_title(href) or parse_type_id_title(label_text)
        if parsed:
            content_type, content_id, parsed_title = parsed
            title = parsed_title
        else:
            content_type = "Index"
            content_id = f"{len(items) + 1:04d}"
            title = label_text or href.split("/")[-1]

        key = (content_type, content_id)
        if key in used_keys:
            continue
        used_keys.add(key)

        items.append(
            {
                "type": content_type,
                "id": content_id,
                "title": title,
                "created": date,
                "createdDate": date,
                "published": date,
                "updated": date,
                "updatedDate": date,
                "slug": f"{content_type.lower()}-{content_id}",
                "href": normalize_legacy_href(href, root),
                "label": f"[{content_type}][{content_id}][{title}]" if content_type != "Index" else title,
                "source": "legacy-index",
                "summary": title,
                "summarySource": "derived",
                "fieldIds": [],
                "mappingSource": "unmapped",
            }
        )
    return items


def collect_markdown_items(root: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    narrative_contract = load_narrative_contract(root)
    for path in sorted((root / "qrthoughts").rglob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        text = read_text(path)
        data = parse_front_matter(text)
        if not data or data.get("status") != "published":
            continue
        required = ["type", "id", "title", "created_date", "published", "updated_date"]
        if any(not data.get(field) for field in required):
            raise ValueError(f"Missing required front matter in {path}")
        source_path = path.relative_to(root).as_posix()
        legacy_href = render_href(path, root)
        canonical_href = clean_article_href(data["type"], data["id"])
        body = markdown_body(text)
        explicit_summary = data.get("summary", "").strip()
        summary = explicit_summary or markdown_excerpt(body) or data["title"]
        summary_source = "explicit" if explicit_summary else "derived"
        tags = parse_list(data.get("tags", ""))
        series = data.get("series", "").strip()
        field_ids, mapping_source = resolve_narrative_mapping(data, narrative_contract, source_path)
        math_enabled = parse_bool(data.get("math", "")) or detects_math(body)
        interactive_enabled = parse_bool(data.get("interactive", "")) or detects_interactive(body)
        lead_image = normalize_lead_image(data.get("lead_image", ""), path, root) or first_markdown_image(body, path, root)
        item = {
                "type": data["type"],
                "id": data["id"],
                "title": data["title"],
                "created": data.get("created", data["created_date"]),
                "createdDate": data["created_date"],
                "published": data["published"],
                "updated": data.get("updated", data["updated_date"]),
                "updatedDate": data["updated_date"],
                "slug": data.get("slug", ""),
                "href": canonical_href,
                "canonicalHref": canonical_href,
                "legacyHref": legacy_href,
                "sourcePath": source_path,
                "label": f"[{data['type']}][{data['id']}][{data['title']}]",
                "source": "markdown",
                "summarySource": summary_source,
                "fieldIds": field_ids,
                "mappingSource": mapping_source,
            }
        if summary:
            item["summary"] = summary
        if tags:
            item["tags"] = tags
        if series:
            item["series"] = series
        if math_enabled:
            item["math"] = True
        if interactive_enabled:
            item["interactive"] = True
        if lead_image:
            item["leadImage"] = lead_image
        project_revision_fields(item, data)
        items.append(item)

    return items


def collect_items(root: Path, include_legacy_index: bool = False) -> list[dict[str, str]]:
    markdown_items = collect_markdown_items(root)
    if not include_legacy_index:
        markdown_items.sort(key=item_sort_key, reverse=True)
        return markdown_items

    markdown_keys = {(item["type"], item["id"]) for item in markdown_items}
    legacy_items = [
        item for item in parse_legacy_index_items(root)
        if (item["type"], item["id"]) not in markdown_keys
    ]
    items = markdown_items + legacy_items
    items.sort(key=item_sort_key, reverse=True)
    return items


def build_js(items: list[dict[str, str]]) -> str:
    by_type: dict[str, int] = {}
    years: dict[str, int] = {}
    summary_sources = {"explicit": 0, "derived": 0}
    narrative_by_field: dict[str, int] = {}
    narrative_by_source = {source: 0 for source in sorted(MAPPING_SOURCES)}
    mapped = 0
    for item in items:
        by_type[item["type"]] = by_type.get(item["type"], 0) + 1
        years[item["published"][:4]] = years.get(item["published"][:4], 0) + 1
        summary_source = item.get("summarySource", "derived")
        if summary_source in summary_sources:
            summary_sources[summary_source] += 1
        mapping_source = item.get("mappingSource", "unmapped")
        if mapping_source in narrative_by_source:
            narrative_by_source[mapping_source] += 1
        field_ids = item.get("fieldIds") or []
        if field_ids:
            mapped += 1
        for field_id in field_ids:
            narrative_by_field[field_id] = narrative_by_field.get(field_id, 0) + 1
    generated_at = max(
        (item.get("updatedDate") or item.get("published") or item.get("createdDate") for item in items),
        default="",
    )

    payload = {
        "generatedAt": generated_at,
        "items": items,
        "stats": {
            "total": len(items),
            "byType": by_type,
            "years": dict(sorted(years.items(), reverse=True)),
            "summaries": summary_sources,
            "narrativeCoverage": {
                "mapped": mapped,
                "total": len(items),
                "unmapped": len(items) - mapped,
                "percent": round((mapped / len(items) * 100), 1) if items else 0.0,
                "byField": narrative_by_field,
                "bySource": narrative_by_source,
            },
        },
    }
    return "window.HOMEPAGE_DATA = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out", default="homepage-data.js", help="Output JS file.")
    parser.add_argument(
        "--include-legacy-index",
        action="store_true",
        help="Merge legacy index-data.js entries that do not yet have Markdown sources.",
    )
    return parser


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = build_arg_parser().parse_args(argv)
    root = Path(args.root).resolve()
    items = collect_items(root, include_legacy_index=args.include_legacy_index)
    out = root / args.out
    out.write_text(build_js(items), encoding="utf-8", newline="\n")
    print(f"Generated {out} with {len(items)} items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
