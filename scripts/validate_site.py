#!/usr/bin/env python3
"""Validate generated Markdown article URLs and alias pages."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path


DATA_RE = re.compile(r"^\s*window\.HOMEPAGE_DATA\s*=\s*(?P<payload>[\s\S]*?)\s*;\s*$")
ARTICLE_CONFIG_RE = re.compile(
    r'<script\s+type="application/json"\s+id="article-config"\s*>(?P<payload>[\s\S]*?)</script>',
    re.I,
)
ARTICLE_TYPES = {"Books", "Thoughts", "Study", "Videos"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_homepage_data(root: Path) -> dict:
    data_path = root / "homepage-data.js"
    text = read_text(data_path)
    match = DATA_RE.match(text)
    if not match:
        raise ValueError(f"{data_path} does not contain window.HOMEPAGE_DATA JSON")
    return json.loads(match.group("payload"))


def alias_path_for(root: Path, item: dict[str, str]) -> Path:
    href = item.get("href", "")
    return root / href.lstrip("/") / "index.html"


def expected_clean_href(item: dict[str, str]) -> str:
    return f"/{item.get('type', '').lower()}/{item.get('id', '')}/"


def is_clean_href(href: str) -> bool:
    return bool(re.fullmatch(r"/[a-z]+/\d{4}/", href))


def load_article_config(alias_path: Path) -> dict[str, str]:
    text = read_text(alias_path)
    match = ARTICLE_CONFIG_RE.search(text)
    if not match:
        raise ValueError("missing article-config script")
    payload = html.unescape(match.group("payload"))
    return json.loads(payload)


def validate_item(root: Path, item: dict[str, str]) -> list[str]:
    errors: list[str] = []
    label = f"{item.get('type', '<missing-type>')} {item.get('id', '<missing-id>')}"

    href = item.get("href")
    canonical = item.get("canonicalHref")
    legacy = item.get("legacyHref")
    source_path = item.get("sourcePath")

    if not href:
        errors.append(f"{label}: missing href")
    elif not is_clean_href(href):
        errors.append(f"{label}: href is not a clean URL: {href}")
    elif href != expected_clean_href(item):
        errors.append(f"{label}: href does not match type/id: {href} != {expected_clean_href(item)}")

    if canonical != href:
        errors.append(f"{label}: canonicalHref does not equal href: {canonical} != {href}")

    if not legacy:
        errors.append(f"{label}: missing legacyHref")
    elif not legacy.startswith("render.html?md="):
        errors.append(f"{label}: legacyHref is not render.html?md: {legacy}")

    if not source_path:
        errors.append(f"{label}: missing sourcePath")
    else:
        md_path = root / source_path.lstrip("/")
        if not md_path.exists():
            errors.append(f"{label}: sourcePath does not exist: {source_path}")

    if item.get("type") not in ARTICLE_TYPES:
        errors.append(f"{label}: unsupported article type for alias page: {item.get('type')}")
        return errors

    if href:
        alias_path = alias_path_for(root, item)
        if not alias_path.exists():
            errors.append(f"{label}: alias page does not exist: {alias_path.relative_to(root).as_posix()}")
        else:
            try:
                config = load_article_config(alias_path)
            except (ValueError, json.JSONDecodeError) as exc:
                errors.append(f"{label}: cannot read article-config in {alias_path.relative_to(root).as_posix()}: {exc}")
            else:
                expected_md = "/" + (source_path or "").lstrip("/")
                if config.get("md") != expected_md:
                    errors.append(
                        f"{label}: article-config md mismatch in {alias_path.relative_to(root).as_posix()}: "
                        f"{config.get('md')} != {expected_md}"
                    )
                if config.get("canonical") != href:
                    errors.append(
                        f"{label}: article-config canonical mismatch in {alias_path.relative_to(root).as_posix()}: "
                        f"{config.get('canonical')} != {href}"
                    )

    return errors


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--max-errors", type=int, default=25, help="Maximum errors to print before truncating.")
    return parser


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = build_arg_parser().parse_args(argv)
    root = Path(args.root).resolve()

    try:
        data = load_homepage_data(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Site validation failed: cannot load homepage-data.js: {exc}")
        return 1

    items = data.get("items")
    if not isinstance(items, list):
        print("Site validation failed: homepage-data.js has no items array")
        return 1

    markdown_items = [item for item in items if item.get("source") == "markdown"]
    errors: list[str] = []
    for item in markdown_items:
        errors.extend(validate_item(root, item))

    print("Site validation summary")
    print(f"  homepage items: {len(items)}")
    print(f"  markdown items checked: {len(markdown_items)}")
    print(f"  errors: {len(errors)}")

    if errors:
        print()
        print("Failures:")
        for error in errors[: args.max_errors]:
            print(f"  - {error}")
        remaining = len(errors) - args.max_errors
        if remaining > 0:
            print(f"  ... {remaining} more error(s) not shown")
        return 1

    print("  result: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
