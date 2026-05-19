#!/usr/bin/env python3
"""Build generated site data from canonical Markdown notes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import generate_homepage_data
import normalize_markdown_front_matter


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out", default="homepage-data.js", help="Homepage data output.")
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="Add missing front matter to older Markdown files before generating data.",
    )
    parser.add_argument(
        "--include-legacy-index",
        action="store_true",
        help="Also merge legacy index-data.js entries for transition diagnostics.",
    )
    return parser


def pending_front_matter(root: Path) -> list[normalize_markdown_front_matter.MarkdownNote]:
    index_entries = normalize_markdown_front_matter.parse_index_data(root)
    return [
        note
        for path in normalize_markdown_front_matter.find_markdown_notes(root)
        if (note := normalize_markdown_front_matter.derive_note(path, root, index_entries))
    ]


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = build_arg_parser().parse_args(argv)
    root = Path(args.root).resolve()

    notes = pending_front_matter(root)
    if notes and not args.normalize:
        print(f"Markdown notes missing front matter: {len(notes)}")
        for note in notes:
            print(f"  {note.rel_path}")
        print("Run with --normalize to write missing front matter.")
        return 1

    if notes and args.normalize:
        for note in notes:
            normalize_markdown_front_matter.write_text(
                note.path,
                normalize_markdown_front_matter.build_front_matter(note) + note.body.lstrip(),
            )
        print(f"Updated Markdown files: {len(notes)}")

    items = generate_homepage_data.collect_items(root, include_legacy_index=args.include_legacy_index)
    out = root / args.out
    out.write_text(generate_homepage_data.build_js(items), encoding="utf-8", newline="\n")
    print(f"Generated {out} with {len(items)} Markdown-backed items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
