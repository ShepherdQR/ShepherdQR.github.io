#!/usr/bin/env python3
"""Build generated site data from canonical Markdown notes."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

import generate_homepage_data
import normalize_markdown_front_matter


ARTICLE_TYPES = {"Books", "Thoughts", "Study", "Videos"}
SITE_TITLE = "ShepherdQR.github.io"
DEFAULT_SITE_BASE_URL = "https://shepherdqr.github.io"
STATIC_SITEMAP_PATHS = [
    "/",
    "/archive.html",
    "/stats.html",
    "/field.html",
    "/books.html",
    "/series.html",
    "/series/20th-century-world-poetry/",
    "/thoughts.html",
    "/study.html",
    "/videos.html",
]
SITE_PLANE_SOURCE = Path("data/site-plane.json")
SITE_PLANE_OUTPUT = Path("site-data.js")
ARTICLE_TEMPLATE_VERSION = "knowledge-note-v2"


def root_relative_prefix(alias_path: Path, root: Path) -> str:
    rel_parent = alias_path.parent.relative_to(root)
    depth = len(rel_parent.parts)
    return "./" if depth == 0 else "../" * depth


def build_article_alias_html(item: dict[str, str], root: Path, alias_path: Path) -> str:
    prefix = root_relative_prefix(alias_path, root)
    canonical = item["canonicalHref"]
    canonical_url = absolute_url(site_base_url(root), canonical)
    md_path = "/" + item["sourcePath"].lstrip("/")
    math_enabled = bool(item.get("math"))
    interactive_enabled = bool(item.get("interactive"))
    config = json.dumps(
        {
            "md": md_path,
            "canonical": canonical,
            "template": ARTICLE_TEMPLATE_VERSION,
            "math": math_enabled,
            "interactive": interactive_enabled,
        },
        ensure_ascii=False,
        indent=2,
    ).replace("</", "<\\/")

    def asset(path: str) -> str:
        return prefix + path

    title = html.escape(item["title"], quote=False)
    title_attr = html.escape(item["title"], quote=True)
    description_attr = html.escape(item.get("summary") or item["title"], quote=True)
    canonical_attr = html.escape(canonical_url, quote=True)
    lead_image = item.get("leadImage", "")
    lead_image_url = (
        absolute_url(site_base_url(root), lead_image)
        if lead_image and not lead_image.startswith(("http://", "https://", "//"))
        else lead_image
    )
    og_image_tag = (
        f'    <meta property="og:image" content="{html.escape(lead_image_url, quote=True)}">\n'
        if lead_image_url
        else ""
    )
    feature_scripts: list[str] = []
    if interactive_enabled:
        feature_scripts.append(f'    <script src="{asset("includes/js/d3.js")}"></script>')
    if math_enabled:
        feature_scripts.extend(
            [
                "    <script>",
                "        window.MathJax = {",
                "            tex: { inlineMath: [['$', '$'], ['\\\\(', '\\\\)']] }",
                "        };",
                "    </script>",
                '    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>',
            ]
        )
    feature_script_html = "\n".join(feature_scripts)
    if feature_script_html:
        feature_script_html += "\n"

    return f"""<!doctype html>
<html lang="zh-CN" data-theme="field">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="{description_attr}">
    <meta property="og:title" content="{title_attr}">
    <meta property="og:description" content="{description_attr}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{canonical_attr}">
{og_image_tag}    <script src="{asset('includes/js/theme.js')}"></script>
    <link href="{asset('includes/css/pages.css')}" rel="stylesheet" type="text/css">
    <link rel="alternate" type="application/atom+xml" href="{asset('includes/atom.xml')}" title="Atom feed">
    <link rel="shortcut icon" href="{asset('resources/pics/shepherd.png')}">
    <link rel="canonical" href="{html.escape(canonical, quote=True)}">
{feature_script_html}    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <title>{title}</title>
</head>
<body data-template="{ARTICLE_TEMPLATE_VERSION}">
    <a class="skip-link" href="#main-content">跳到主要内容</a>
    <main class="article-shell" id="main-content">
        <nav class="article-nav" aria-label="知识界面导航">
            <a class="article-brand" href="{asset('index.html')}">ZQR.WORLD</a>
            <div class="article-nav-links">
                <a href="{asset('index.html')}">Field</a>
                <a href="{asset('archive.html')}">Atlas</a>
                <a href="{asset('stats.html')}">Evidence</a>
                <a href="{asset('field.html')}">System</a>
                <a href="{asset('series.html')}">Series</a>
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
                    <a href="{asset('index.html')}">Field</a>
                    <a href="{asset('archive.html')}">Atlas</a>
                    <a href="{asset('stats.html')}">Evidence</a>
                    <a href="{asset('field.html')}">System</a>
                    <a href="{asset('series.html')}">Series</a>
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


def site_base_url(root: Path) -> str:
    cname_path = root / "CNAME"
    if cname_path.exists():
        domain = cname_path.read_text(encoding="utf-8", errors="replace").strip()
        if domain:
            return "https://" + domain.rstrip("/")
    return DEFAULT_SITE_BASE_URL


def absolute_url(base_url: str, path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    return base_url.rstrip("/") + path


def latest_date(items: list[dict[str, str]]) -> str:
    return max(
        (item.get("updatedDate") or item.get("published") or item.get("createdDate") for item in items),
        default=dt.date.today().isoformat(),
    )


def atom_datetime(value: str) -> str:
    value = (value or "").strip()
    try:
        if len(value) == 10:
            parsed = dt.datetime.fromisoformat(value + "T00:00:00")
        else:
            parsed = dt.datetime.fromisoformat(value.replace(" ", "T"))
    except ValueError:
        parsed = dt.datetime.fromisoformat(dt.date.today().isoformat() + "T00:00:00")
    return parsed.replace(tzinfo=dt.timezone(dt.timedelta(hours=8))).isoformat()


def build_sitemap_xml(items: list[dict[str, str]], base_url: str) -> str:
    site_lastmod = latest_date(items)
    urls = [
        {"loc": absolute_url(base_url, path), "lastmod": site_lastmod}
        for path in STATIC_SITEMAP_PATHS
    ]
    urls.extend(
        {
            "loc": absolute_url(base_url, item["canonicalHref"]),
            "lastmod": item.get("updatedDate") or item.get("published") or site_lastmod,
        }
        for item in items
        if item.get("source") == "markdown" and item.get("canonicalHref")
    )

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for entry in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{xml_escape(entry['loc'])}</loc>")
        lines.append(f"    <lastmod>{xml_escape(entry['lastmod'])}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def build_atom_xml(items: list[dict[str, str]], base_url: str) -> str:
    updated = atom_datetime(latest_date(items))
    feed_url = absolute_url(base_url, "/includes/atom.xml")
    home_url = absolute_url(base_url, "/")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<feed xmlns="http://www.w3.org/2005/Atom">')
    lines.append(f"  <title>{xml_escape(SITE_TITLE)}</title>")
    lines.append(f'  <link href="{xml_escape(home_url)}" />')
    lines.append(f'  <link rel="self" href="{xml_escape(feed_url)}" />')
    lines.append(f"  <id>{xml_escape(home_url)}</id>")
    lines.append(f"  <updated>{xml_escape(updated)}</updated>")
    lines.append("  <author>")
    lines.append("    <name>Qirong Zhang</name>")
    lines.append("  </author>")

    for item in items[:50]:
        if item.get("source") != "markdown" or not item.get("canonicalHref"):
            continue
        url = absolute_url(base_url, item["canonicalHref"])
        published = atom_datetime(item.get("published", ""))
        entry_updated = atom_datetime(item.get("updated", item.get("updatedDate", "")))
        summary = item.get("summary") or f"{item.get('type', 'Note')} note {item.get('id', '')}"
        lines.append("  <entry>")
        lines.append(f"    <title>{xml_escape(item.get('title', 'Untitled'))}</title>")
        lines.append(f'    <link href="{xml_escape(url)}" />')
        lines.append(f"    <id>{xml_escape(url)}</id>")
        lines.append(f"    <published>{xml_escape(published)}</published>")
        lines.append(f"    <updated>{xml_escape(entry_updated)}</updated>")
        lines.append(f"    <summary>{xml_escape(summary)}</summary>")
        lines.append("  </entry>")

    lines.append("</feed>")
    return "\n".join(lines) + "\n"


def write_site_indexes(root: Path, items: list[dict[str, str]]) -> None:
    base_url = site_base_url(root)
    (root / "sitemap.xml").write_text(build_sitemap_xml(items, base_url), encoding="utf-8", newline="\n")
    atom_path = root / "includes" / "atom.xml"
    atom_path.parent.mkdir(parents=True, exist_ok=True)
    atom_path.write_text(build_atom_xml(items, base_url), encoding="utf-8", newline="\n")


def write_site_plane_data(root: Path) -> dict:
    source_path = root / SITE_PLANE_SOURCE
    if not source_path.exists():
        raise FileNotFoundError(f"Missing public site-plane source: {source_path}")

    payload = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("data/site-plane.json must contain a JSON object")

    output = "window.SITE_PLANE = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n"
    (root / SITE_PLANE_OUTPUT).write_text(output, encoding="utf-8", newline="\n")
    return payload


def build_generated_site(root: Path, out_name: str, include_legacy_index: bool = False) -> tuple[int, int]:
    items = generate_homepage_data.collect_items(root, include_legacy_index=include_legacy_index)
    out = root / out_name
    out.write_text(generate_homepage_data.build_js(items), encoding="utf-8", newline="\n")
    alias_count = write_article_alias_pages(root, items)
    write_site_indexes(root, items)
    write_site_plane_data(root)
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
                normalize_markdown_front_matter.insert_front_matter_after_leading_comments(note),
            )
        print(f"Updated Markdown files: {len(notes)}")

    item_count, alias_count = build_generated_site(
        root,
        args.out,
        include_legacy_index=args.include_legacy_index,
    )
    print(f"Generated {root / args.out} with {item_count} Markdown-backed items")
    print(f"Generated {alias_count} article alias pages")
    print("Generated sitemap.xml")
    print("Generated includes/atom.xml")
    print("Generated site-data.js")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
