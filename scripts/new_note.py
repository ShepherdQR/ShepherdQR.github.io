#!/usr/bin/env python3
"""Create a new Markdown note with canonical front matter."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import build_site


TYPE_VALUES = ("Books", "Thoughts", "Study", "Videos")
FRONT_MATTER_FIELD_RE = re.compile(r"^(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?P<value>.*)$")


def parse_existing_id(path: Path, content_type: str) -> int | None:
    match = re.match(rf"^\[{re.escape(content_type)}\]\[(\d{{4}})\]", path.stem)
    if match:
        return int(match.group(1))
    return None


def parse_yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return value


def parse_front_matter_fields(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}

    match = re.match(r"^---\s*\n(?P<yaml>[\s\S]*?)\n---\s*\n", text)
    if not match:
        return {}

    fields: dict[str, str] = {}
    for line in match.group("yaml").splitlines():
        if line.startswith(" ") or not line.strip():
            continue
        field = FRONT_MATTER_FIELD_RE.match(line)
        if field:
            fields[field.group("key")] = parse_yaml_scalar(field.group("value"))
    return fields


def parse_markdown_id(path: Path, content_type: str) -> int | None:
    fields = parse_front_matter_fields(path)
    if fields.get("type") == content_type and re.match(r"^\d{4}$", fields.get("id", "")):
        return int(fields["id"])
    return parse_existing_id(path, content_type)


def next_id(root: Path, content_type: str) -> str:
    ids: list[int] = []
    for path in (root / "qrthoughts").rglob("*.md"):
        if path.name.lower() == "readme.md":
            continue
        if value := parse_markdown_id(path, content_type):
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


def yaml_list(values: list[str]) -> str:
    return "[" + ", ".join(yaml_quote(value) for value in values) + "]"


def split_values(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def build_markdown(
    content_type: str,
    content_id: str,
    title: str,
    now: str,
    date: str,
    status: str,
    tags: list[str],
    series: str | None,
    summary: str | None,
) -> str:
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
    ]
    if tags:
        lines.append(f"tags: {yaml_list(tags)}")
    if series:
        lines.append(f"series: {yaml_quote(series)}")
    if summary:
        lines.append(f"summary: {yaml_quote(summary)}")
    lines.extend(
        [
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
    )
    return "\n".join(lines)


def open_note(path: Path) -> None:
    try:
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except (AttributeError, FileNotFoundError, OSError) as exc:
        print(f"Could not open editor for {path}: {exc}", file=sys.stderr)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("type", choices=TYPE_VALUES, help="Content type.")
    parser.add_argument("title", help="Human-readable note title.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--id", help="Four-digit id. Defaults to the next id for the type.")
    parser.add_argument("--date", help="Publication date YYYY-MM-DD. Defaults to today.")
    parser.add_argument("--status", default="published", choices=("draft", "published", "doing", "archived"))
    parser.add_argument("--tags", help="Comma-separated tags to write into front matter.")
    parser.add_argument("--series", help="Series name to write into front matter.")
    parser.add_argument("--summary", help="Short summary to write into front matter.")
    parser.add_argument("--open", action="store_true", help="Open the new Markdown file with the system default app.")
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
        build_markdown(
            args.type,
            content_id,
            args.title,
            now,
            note_date,
            args.status,
            split_values(args.tags),
            args.series,
            args.summary,
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(f"Created {target.relative_to(root).as_posix()}")
    print(f"Canonical URL: /{args.type.lower()}/{content_id}/")

    if not args.no_build:
        item_count, alias_count = build_site.build_generated_site(root, "homepage-data.js")
        print(f"Regenerated homepage-data.js with {item_count} Markdown-backed items")
        print(f"Generated {alias_count} article alias pages")

    if args.open:
        open_note(target)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
