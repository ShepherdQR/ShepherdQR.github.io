#!/usr/bin/env python3
"""Create a new Markdown note with canonical front matter."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import unicodedata
from pathlib import Path

import generate_homepage_data


TYPE_VALUES = ("Books", "Thoughts", "Study", "Videos")


def parse_existing_id(path: Path, content_type: str) -> int | None:
    match = re.match(rf"^\[{re.escape(content_type)}\]\[(\d{{4}})\]", path.stem)
    if match:
        return int(match.group(1))
    return None


def next_id(root: Path, content_type: str) -> str:
    ids: list[int] = []
    for suffix in ("*.md", "*.html"):
        for path in (root / "qrthoughts").rglob(suffix):
            if value := parse_existing_id(path, content_type):
                ids.append(value)
    return f"{(max(ids) if ids else 0) + 1:04d}"


def slugify(title: str, content_type: str, content_id: str) -> str:
    normalized = unicodedata.normalize("NFKD", title)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    if len(slug) < 4 or slug.isdigit():
        return f"{content_type.lower()}-{content_id}"
    return slug


def safe_title_for_filename(title: str) -> str:
    return re.sub(r'[<>:"/\\|?*\r\n]+', "_", title).strip() or "untitled"


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_markdown(content_type: str, content_id: str, title: str, now: str, date: str, status: str) -> str:
    slug = slugify(title, content_type, content_id)
    lines = [
        "---",
        f"type: {content_type}",
        f"id: {yaml_quote(content_id)}",
        f"title: {yaml_quote(title)}",
        f"created: {yaml_quote(now)}",
        f"created_date: {yaml_quote(date)}",
        f"published: {yaml_quote(date)}",
        f"updated: {yaml_quote(now)}",
        f"updated_date: {yaml_quote(date)}",
        f"slug: {yaml_quote(slug)}",
        f"status: {yaml_quote(status)}",
        "source:",
        "  date_source:",
        '    created: "new-note"',
        '    published: "new-note"',
        '    updated: "new-note"',
        "---",
        "",
        f"# {title}",
        "",
    ]
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("type", choices=TYPE_VALUES, help="Content type.")
    parser.add_argument("title", help="Human-readable note title.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--id", help="Four-digit id. Defaults to the next id for the type.")
    parser.add_argument("--date", help="Publication date YYYY-MM-DD. Defaults to today.")
    parser.add_argument("--status", default="published", choices=("draft", "published", "doing", "archived"))
    parser.add_argument("--no-build", action="store_true", help="Create the note without regenerating homepage data.")
    return parser


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = build_arg_parser().parse_args(argv)
    root = Path(args.root).resolve()
    now_dt = dt.datetime.now().replace(microsecond=0)
    note_date = args.date or now_dt.date().isoformat()
    now = f"{note_date} {now_dt.strftime('%H:%M:%S')}"
    content_id = args.id or next_id(root, args.type)

    if not re.match(r"^\d{4}$", content_id):
        raise ValueError("--id must be four digits")

    year, month = note_date.split("-")[:2]
    target = (
        root
        / "qrthoughts"
        / f"year{year}"
        / f"month{int(month)}"
        / f"[{args.type}][{content_id}][{safe_title_for_filename(args.title)}].md"
    )
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite existing note: {target}")

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        build_markdown(args.type, content_id, args.title, now, note_date, args.status),
        encoding="utf-8",
        newline="\n",
    )
    print(f"Created {target.relative_to(root).as_posix()}")

    if not args.no_build:
        items = generate_homepage_data.collect_items(root)
        (root / "homepage-data.js").write_text(generate_homepage_data.build_js(items), encoding="utf-8", newline="\n")
        print(f"Regenerated homepage-data.js with {len(items)} Markdown-backed items")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
