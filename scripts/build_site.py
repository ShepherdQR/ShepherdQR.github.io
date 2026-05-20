#!/usr/bin/env python3
"""Build generated site data from canonical Markdown notes."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

import generate_homepage_data
import normalize_markdown_front_matter


ARTICLE_TYPES = {"Books", "Thoughts", "Study", "Videos"}


def root_relative_prefix(alias_path: Path, root: Path) -> str:
    rel_parent = alias_path.parent.relative_to(root)
    depth = len(rel_parent.parts)
    return "./" if depth == 0 else "../" * depth


def build_article_alias_html(item: dict[str, str], root: Path, alias_path: Path) -> str:
    prefix = root_relative_prefix(alias_path, root)
    canonical = item["canonicalHref"]
    md_path = "/" + item["sourcePath"].lstrip("/")
    config = json.dumps(
        {
            "md": md_path,
            "canonical": canonical,
        },
        ensure_ascii=False,
        indent=2,
    ).replace("</", "<\\/")

    def asset(path: str) -> str:
        return prefix + path

    title = html.escape(item["title"], quote=False)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="{asset('includes/css/pages.css')}" rel="stylesheet" type="text/css">
    <link rel="alternate" type="application/atom+xml" href="{asset('includes/atom.xml')}" title="Atom feed">
    <link rel="shortcut icon" href="{asset('resources/pics/shepherd.png')}">
    <link rel="canonical" href="{html.escape(canonical, quote=True)}">
    <script src="{asset('includes/js/d3.js')}"></script>
    <script>
        window.MathJax = {{
            tex: {{ inlineMath: [['$', '$'], ['\\\\(', '\\\\)']] }}
        }};
    </script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <title>{title}</title>
</head>
<body>
    <main class="article-shell">
        <nav class="article-nav" aria-label="Article navigation">
            <a class="article-brand" href="{asset('index.html')}">ShepherdQR.github.io</a>
            <div class="article-nav-links">
                <a href="{asset('archive.html')}">Archive</a>
                <a href="{asset('stats.html')}">Stats</a>
                <a href="{asset('books.html')}">Books</a>
                <a href="{asset('thoughts.html')}">Thoughts</a>
            </div>
        </nav>

        <article class="article-frame">
            <header class="article-header">
                <p id="currentInnerType" class="article-kicker"></p>
                <h1 id="currentInnerTitle"></h1>
                <div id="currentInnerMeta" class="article-meta"></div>
            </header>
            <div id="markdown-content" class="article-content" aria-live="polite"></div>
            <footer class="article-footer">
                <div class="article-footer-links">
                    <a href="{asset('index.html')}">Home</a>
                    <a href="{asset('archive.html')}">Archive</a>
                    <a href="{asset('stats.html')}">Stats</a>
                    <a href="{asset('books.html')}">Books</a>
                    <a href="{asset('thoughts.html')}">Thoughts</a>
                    <a href="{asset('study.html')}">Study</a>
                    <a href="{asset('videos.html')}">Videos</a>
                </div>
                <nav id="article-neighbors" class="article-neighbors" aria-label="Adjacent notes"></nav>
            </footer>
        </article>
    </main>

    <script type="application/json" id="article-config">{config}</script>
    <script src="{asset('homepage-data.js')}"></script>
    <script src="{asset('includes/js/article-renderer.js')}"></script>
</body>
</html>
"""


def alias_path_for_item(root: Path, item: dict[str, str]) -> Path:
    return root / item["type"].lower() / item["id"] / "index.html"


def write_article_alias_pages(root: Path, items: list[dict[str, str]]) -> int:
    alias_items = [
        item for item in items
        if item.get("source") == "markdown" and item.get("type") in ARTICLE_TYPES
    ]
    seen: dict[str, str] = {}
    for item in alias_items:
        canonical = item["canonicalHref"]
        source_path = item["sourcePath"]
        if canonical in seen:
            raise ValueError(f"Duplicate canonical URL {canonical}: {seen[canonical]} and {source_path}")
        seen[canonical] = source_path

    for item in alias_items:
        alias_path = alias_path_for_item(root, item)
        alias_path.parent.mkdir(parents=True, exist_ok=True)
        alias_path.write_text(build_article_alias_html(item, root, alias_path), encoding="utf-8", newline="\n")

    missing = [item["canonicalHref"] for item in alias_items if not alias_path_for_item(root, item).exists()]
    if missing:
        raise RuntimeError("Missing generated alias pages: " + ", ".join(missing[:10]))

    return len(alias_items)


def build_generated_site(root: Path, out_name: str, include_legacy_index: bool = False) -> tuple[int, int]:
    items = generate_homepage_data.collect_items(root, include_legacy_index=include_legacy_index)
    out = root / out_name
    out.write_text(generate_homepage_data.build_js(items), encoding="utf-8", newline="\n")
    alias_count = write_article_alias_pages(root, items)
    return len(items), alias_count


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

    item_count, alias_count = build_generated_site(
        root,
        args.out,
        include_legacy_index=args.include_legacy_index,
    )
    print(f"Generated {root / args.out} with {item_count} Markdown-backed items")
    print(f"Generated {alias_count} article alias pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
