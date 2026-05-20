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
INDEX_ITEM_RE = re.compile(
    r"\{\s*date:\s*'(?P<date>[^']+)'\s*,\s*href:\s*'(?P<href>(?:\\'|[^'])*)'\s*,\s*text:\s*(?:'(?P<text1>(?:\\'|[^'])*)'|\"(?P<text2>(?:\\\"|[^\"])*)\")",
    re.S,
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return value


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
            }
        )
    return items


def collect_markdown_items(root: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for path in sorted((root / "qrthoughts").rglob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        data = parse_front_matter(read_text(path))
        if not data or data.get("status") != "published":
            continue
        required = ["type", "id", "title", "created_date", "published", "updated_date"]
        if any(not data.get(field) for field in required):
            raise ValueError(f"Missing required front matter in {path}")
        source_path = path.relative_to(root).as_posix()
        legacy_href = render_href(path, root)
        canonical_href = clean_article_href(data["type"], data["id"])
        items.append(
            {
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
            }
        )

    return items


def collect_items(root: Path, include_legacy_index: bool = False) -> list[dict[str, str]]:
    markdown_items = collect_markdown_items(root)
    if not include_legacy_index:
        markdown_items.sort(key=lambda item: (item["published"], item["id"]), reverse=True)
        return markdown_items

    markdown_keys = {(item["type"], item["id"]) for item in markdown_items}
    legacy_items = [
        item for item in parse_legacy_index_items(root)
        if (item["type"], item["id"]) not in markdown_keys
    ]
    items = markdown_items + legacy_items
    items.sort(key=lambda item: (item["published"], item["id"]), reverse=True)
    return items


def build_js(items: list[dict[str, str]]) -> str:
    by_type: dict[str, int] = {}
    years: dict[str, int] = {}
    for item in items:
        by_type[item["type"]] = by_type.get(item["type"], 0) + 1
        years[item["published"][:4]] = years.get(item["published"][:4], 0) + 1
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
