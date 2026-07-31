#!/usr/bin/env python3
"""Build durable, semantic article HTML from repository Markdown.

The public article aliases use this renderer as their baseline.  JavaScript may
enhance the resulting document, but it is never required to retrieve or read
the article body.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import struct
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

import generate_homepage_data


ARTICLE_FORMS = {"exposition", "research-log", "visual-essay", "reading"}
IMAGE_MANIFEST_PATH = Path("resources/pics/derivatives/manifest.json")
HEADING_RE = re.compile(r"^(?P<indent>\s{0,3})(?P<marks>#{1,6})\s+(?P<title>.*?)(?:\s+#+\s*)?$")
FENCE_RE = re.compile(r"^\s*(```+|~~~+)\s*([^\s`]*)?.*$")
TABLE_DIVIDER_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")
LIST_RE = re.compile(r"^\s{0,3}(?P<marker>[-+*]|\d+[.)])\s+(?P<body>.+)$")
RAW_BLOCK_TAG_RE = re.compile(
    r"^\s*</?(?:address|article|aside|blockquote|canvas|details|dialog|div|dl|fieldset|figure|footer|form|h[1-6]|header|hr|iframe|main|nav|noscript|ol|p|pre|script|section|style|summary|svg|table|ul)\b",
    re.I,
)
SAFE_INLINE_HTML_RE = re.compile(
    r"</?(?:abbr|b|br|cite|code|del|em|i|ins|kbd|mark|q|s|small|span|strong|sub|sup|time|u|var)(?:\s+[^<>]*?)?/?>",
    re.I,
)


@dataclass
class RenderedArticle:
    body_html: str
    headings: list[dict[str, str | int]] = field(default_factory=list)
    image_paths: list[str] = field(default_factory=list)
    local_truth_charter_present: bool = False


def read_markdown_document(path: Path) -> tuple[dict[str, str], str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    meta = generate_homepage_data.parse_front_matter(text) or {}
    body = generate_homepage_data.markdown_body(text)
    return meta, body, text


def article_form(item: dict, meta: dict[str, str], body: str) -> str:
    declared = (
        meta.get("article_form")
        or meta.get("form")
        or meta.get("template_variant")
        or ""
    ).strip().lower()
    if declared in ARTICLE_FORMS:
        return declared

    content_type = item.get("type", "")
    tags = {str(tag).strip().lower() for tag in item.get("tags", [])}
    image_count = len(generate_homepage_data.MARKDOWN_IMAGE_RE.findall(body))
    if content_type == "Books":
        return "reading"
    if content_type == "Videos" or image_count >= 2:
        return "visual-essay"
    if content_type == "Study" or tags.intersection(
        {"research", "evaluation", "software-engineering", "experiment", "agent"}
    ):
        return "research-log"
    return "exposition"


def article_governance(item: dict, meta: dict[str, str], source_path: str) -> dict[str, str]:
    return {
        "source": meta.get("provenance", "Repository-authored Markdown"),
        "sourcePath": source_path,
        "revision": meta.get("revision", item.get("updatedDate") or item.get("published") or "Unspecified"),
        "errata": meta.get("errata", "None declared"),
        "supersedes": meta.get("supersedes", "None declared"),
        "supersededBy": meta.get("superseded_by", "None declared"),
        "status": meta.get("status", "published"),
    }


def content_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def load_image_manifest(root: Path) -> dict:
    path = root / IMAGE_MANIFEST_PATH
    if not path.exists():
        return {"assets": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"assets": {}}
    if not isinstance(payload, dict) or not isinstance(payload.get("assets"), dict):
        return {"assets": {}}
    return payload


def image_dimensions(path: Path) -> tuple[int, int] | None:
    """Read common raster dimensions without importing an imaging library."""
    try:
        with path.open("rb") as stream:
            head = stream.read(32)
            if head.startswith(b"\x89PNG\r\n\x1a\n") and len(head) >= 24:
                return struct.unpack(">II", head[16:24])
            if head[:6] in {b"GIF87a", b"GIF89a"} and len(head) >= 10:
                return struct.unpack("<HH", head[6:10])
            if head.startswith(b"RIFF") and head[8:12] == b"WEBP":
                chunk = head[12:16]
                if chunk == b"VP8X" and len(head) >= 30:
                    return (
                        1 + int.from_bytes(head[24:27], "little"),
                        1 + int.from_bytes(head[27:30], "little"),
                    )
                if chunk == b"VP8L" and len(head) >= 25:
                    bits = int.from_bytes(head[21:25], "little")
                    return ((bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1)
            if head.startswith(b"\xff\xd8"):
                stream.seek(2)
                while True:
                    byte = stream.read(1)
                    if not byte:
                        return None
                    if byte != b"\xff":
                        continue
                    marker = stream.read(1)
                    while marker == b"\xff":
                        marker = stream.read(1)
                    if not marker or marker in {b"\xd8", b"\xd9"}:
                        continue
                    size_raw = stream.read(2)
                    if len(size_raw) != 2:
                        return None
                    size = struct.unpack(">H", size_raw)[0]
                    if marker[0] in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                        segment = stream.read(5)
                        if len(segment) != 5:
                            return None
                        height, width = struct.unpack(">HH", segment[1:5])
                        return width, height
                    stream.seek(max(0, size - 2), 1)
    except OSError:
        return None
    return None


class MarkdownRenderer:
    def __init__(self, root: Path, source_path: Path, page_title: str, image_manifest: dict | None = None):
        self.root = root.resolve()
        self.source_path = source_path.resolve()
        self.page_title = self._plain_heading(page_title)
        self.manifest = image_manifest or {"assets": {}}
        self.headings: list[dict[str, str | int]] = []
        self.image_paths: list[str] = []
        self.local_truth_charter_present = False
        self._slug_counts: dict[str, int] = {}
        self._heading_shift = 1
        self._image_index = 0

    def render(self, body: str) -> RenderedArticle:
        lines = body.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        self._heading_shift = self._calculate_heading_shift(lines)
        output: list[str] = []
        index = 0
        while index < len(lines):
            line = lines[index]
            if not line.strip():
                index += 1
                continue

            if line.lstrip().startswith("<!--"):
                while index < len(lines):
                    finished = "-->" in lines[index]
                    index += 1
                    if finished:
                        break
                continue

            fence = FENCE_RE.match(line)
            if fence:
                html_block, index = self._render_fence(lines, index, fence)
                output.append(html_block)
                continue

            heading = HEADING_RE.match(line)
            if heading:
                title = heading.group("title").strip()
                if self._is_page_title(title):
                    index += 1
                    continue
                source_level = len(heading.group("marks"))
                level = min(6, max(2, source_level + self._heading_shift))
                plain = self._plain_heading(title)
                slug = self._unique_slug(plain)
                self.headings.append({"level": level, "id": slug, "text": plain})
                output.append(f'<h{level} id="{html.escape(slug, quote=True)}">{self._inline(title)}</h{level}>')
                index += 1
                continue

            if re.match(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$", line):
                output.append("<hr>")
                index += 1
                continue

            if line.lstrip().startswith(">"):
                block: list[str] = []
                while index < len(lines) and (lines[index].lstrip().startswith(">") or not lines[index].strip()):
                    current = lines[index]
                    block.append(re.sub(r"^\s*>\s?", "", current) if current.strip() else "")
                    index += 1
                paragraphs = self._render_simple_paragraphs(block)
                output.append(f"<blockquote>{paragraphs}</blockquote>")
                continue

            list_match = LIST_RE.match(line)
            if list_match:
                list_html, index = self._render_list(lines, index, ordered=list_match.group("marker")[0].isdigit())
                output.append(list_html)
                continue

            if index + 1 < len(lines) and "|" in line and TABLE_DIVIDER_RE.match(lines[index + 1]):
                table_html, index = self._render_table(lines, index)
                output.append(table_html)
                continue

            if RAW_BLOCK_TAG_RE.match(line):
                raw, index = self._render_raw_block(lines, index)
                output.append(raw)
                continue

            paragraph: list[str] = [line]
            index += 1
            while index < len(lines) and lines[index].strip() and not self._starts_block(lines, index):
                paragraph.append(lines[index])
                index += 1
            joined = "\n".join(paragraph)
            output.append(f"<p>{self._inline(joined, preserve_breaks=True)}</p>")

        return RenderedArticle(
            body_html="\n".join(output),
            headings=self.headings,
            image_paths=self.image_paths,
            local_truth_charter_present=self.local_truth_charter_present,
        )

    def _calculate_heading_shift(self, lines: list[str]) -> int:
        levels = []
        in_fence = False
        fence_char = ""
        for line in lines:
            fence = FENCE_RE.match(line)
            if fence:
                marker = fence.group(1)[0]
                if not in_fence:
                    in_fence = True
                    fence_char = marker
                elif marker == fence_char:
                    in_fence = False
                continue
            if in_fence:
                continue
            heading = HEADING_RE.match(line)
            if heading and not self._is_page_title(heading.group("title")):
                levels.append(len(heading.group("marks")))
        return 2 - min(levels) if levels else 1

    def _starts_block(self, lines: list[str], index: int) -> bool:
        line = lines[index]
        return bool(
            FENCE_RE.match(line)
            or HEADING_RE.match(line)
            or LIST_RE.match(line)
            or line.lstrip().startswith(">")
            or line.lstrip().startswith("<!--")
            or RAW_BLOCK_TAG_RE.match(line)
            or re.match(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$", line)
            or (index + 1 < len(lines) and "|" in line and TABLE_DIVIDER_RE.match(lines[index + 1]))
        )

    def _render_fence(self, lines: list[str], index: int, opening: re.Match) -> tuple[str, int]:
        marker = opening.group(1)
        language = (opening.group(2) or "").strip()
        index += 1
        code: list[str] = []
        while index < len(lines) and not re.match(rf"^\s*{re.escape(marker[0])}{{{len(marker)},}}\s*$", lines[index]):
            code.append(lines[index].rstrip())
            index += 1
        if index < len(lines):
            index += 1
        class_attr = f' class="language-{html.escape(language, quote=True)}"' if language else ""
        return f"<pre><code{class_attr}>{html.escape(chr(10).join(code))}</code></pre>", index

    def _render_list(self, lines: list[str], index: int, ordered: bool) -> tuple[str, int]:
        tag = "ol" if ordered else "ul"
        items: list[str] = []
        while index < len(lines):
            match = LIST_RE.match(lines[index])
            if not match or match.group("marker")[0].isdigit() != ordered:
                break
            body = match.group("body").strip()
            task = re.match(r"^\[([ xX])\]\s+(.*)$", body)
            if task:
                checked = " checked" if task.group(1).lower() == "x" else ""
                rendered = f'<input type="checkbox" disabled{checked}> {self._inline(task.group(2))}'
                items.append(f'<li class="task-list-item">{rendered}</li>')
            else:
                items.append(f"<li>{self._inline(body)}</li>")
            index += 1
        return f"<{tag}>" + "".join(items) + f"</{tag}>", index

    def _render_table(self, lines: list[str], index: int) -> tuple[str, int]:
        headers = self._table_cells(lines[index])
        index += 2
        rows: list[list[str]] = []
        while index < len(lines) and lines[index].strip() and "|" in lines[index]:
            rows.append(self._table_cells(lines[index]))
            index += 1
        head = "".join(f"<th scope=\"col\">{self._inline(cell)}</th>" for cell in headers)
        body = "".join(
            "<tr>" + "".join(f"<td>{self._inline(cell)}</td>" for cell in row) + "</tr>"
            for row in rows
        )
        return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>", index

    @staticmethod
    def _table_cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    def _render_raw_block(self, lines: list[str], index: int) -> tuple[str, int]:
        first = lines[index]
        tag_match = re.match(r"^\s*<(?P<tag>[A-Za-z0-9-]+)\b", first)
        if not tag_match:
            return first, index + 1
        tag = tag_match.group("tag").lower()
        if re.search(rf"</{re.escape(tag)}>\s*$", first, flags=re.I) or first.rstrip().endswith("/>"):
            return first, index + 1
        block = [first.rstrip()]
        index += 1
        while index < len(lines):
            block.append(lines[index].rstrip())
            if re.search(rf"</{re.escape(tag)}>\s*$", lines[index], flags=re.I):
                index += 1
                break
            index += 1
        return "\n".join(block), index

    def _render_simple_paragraphs(self, lines: list[str]) -> str:
        paragraphs: list[str] = []
        current: list[str] = []
        for line in [*lines, ""]:
            if line.strip():
                current.append(line)
            elif current:
                paragraphs.append(f"<p>{self._inline(chr(10).join(current), preserve_breaks=True)}</p>")
                current = []
        return "".join(paragraphs)

    def _inline(self, source: str, preserve_breaks: bool = False) -> str:
        placeholders: dict[str, str] = {}

        def hold(fragment: str) -> str:
            token = f"\u0000{len(placeholders)}\u0000"
            placeholders[token] = fragment
            return token

        def code_repl(match: re.Match) -> str:
            return hold(f"<code>{html.escape(match.group(1))}</code>")

        working = re.sub(r"`([^`\n]+)`", code_repl, source)
        working = SAFE_INLINE_HTML_RE.sub(lambda match: hold(match.group(0)), working)

        image_pattern = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<target><[^>]+>|[^\s)]+)(?:\s+[\"'](?P<title>.*?)[\"'])?\)")
        working = image_pattern.sub(
            lambda match: hold(self._render_image(match.group("alt"), match.group("target"), match.group("title") or "")),
            working,
        )
        link_pattern = re.compile(r"\[(?P<label>[^\]]+)\]\((?P<target><[^>]+>|[^\s)]+)(?:\s+[\"'](?P<title>.*?)[\"'])?\)")

        def link_repl(match: re.Match) -> str:
            target = match.group("target").strip("<>")
            return hold(self._render_link(match.group("label"), target, match.group("title") or ""))

        working = link_pattern.sub(link_repl, working)
        working = re.sub(
            r"<((?:https?://|mailto:)[^>]+)>",
            lambda match: hold(f'<a href="{html.escape(match.group(1), quote=True)}">{html.escape(match.group(1))}</a>'),
            working,
        )
        working = html.escape(working, quote=False)
        working = re.sub(r"\*\*([^*\n]+)\*\*|__([^_\n]+)__", lambda match: f"<strong>{match.group(1) or match.group(2)}</strong>", working)
        working = re.sub(r"~~([^~\n]+)~~", r"<del>\1</del>", working)
        working = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)|(?<!_)_([^_\n]+)_(?!_)", lambda match: f"<em>{match.group(1) or match.group(2)}</em>", working)
        if preserve_breaks:
            working = working.replace("  \n", "<br>\n").replace("\n", " ")
        for token, fragment in placeholders.items():
            working = working.replace(html.escape(token), fragment)
        return working.strip()

    def _render_link(self, label: str, target: str, title: str) -> str:
        title_attr = f' title="{html.escape(title, quote=True)}"' if title else ""
        parsed = urlsplit(target)
        public_target = target
        is_valid = bool(parsed.scheme or target.startswith(("//", "#")))
        if not is_valid:
            if target.startswith("/"):
                candidate = self.root / target.lstrip("/")
                is_valid = candidate.exists()
            else:
                candidate = (self.source_path.parent / target).resolve()
                try:
                    relative = candidate.relative_to(self.root)
                except ValueError:
                    relative = None
                is_valid = relative is not None and candidate.exists()
                if is_valid and relative is not None:
                    public_target = "/" + relative.as_posix()
        if not is_valid:
            # Several historic note titles use Markdown-looking brackets as
            # typography (for example ``[诗歌译丛](第二辑)``).  Emitting a dead
            # anchor would turn archival notation into a false navigation
            # claim, so preserve the source text as text.
            return html.escape(f"[{label}]({target})")
        return (
            f'<a href="{html.escape(public_target, quote=True)}"{title_attr}>'
            f"{html.escape(label)}</a>"
        )

    def _render_image(self, alt: str, target: str, title: str) -> str:
        self._image_index += 1
        clean_target = target.strip().strip("<>")
        title_attr = f' title="{html.escape(title, quote=True)}"' if title else ""
        if urlsplit(clean_target).scheme or clean_target.startswith("//"):
            return (
                f'<img src="{html.escape(clean_target, quote=True)}" alt="{html.escape(alt, quote=True)}"'
                f'{title_attr} loading="lazy" decoding="async">'
            )

        if clean_target.startswith("/"):
            absolute = self.root / clean_target.lstrip("/")
        else:
            absolute = (self.source_path.parent / clean_target).resolve()
        try:
            relative = absolute.resolve().relative_to(self.root).as_posix()
        except (OSError, ValueError):
            relative = clean_target.replace("\\", "/").lstrip("./")
            absolute = self.root / relative
        public_src = "/" + relative.lstrip("/")
        self.image_paths.append(public_src)

        is_charter = "局部真理宪章" in alt or absolute.name == "topos-asi-shadow-luxury-image-v2.png"
        if is_charter:
            self.local_truth_charter_present = True

        dimensions = image_dimensions(absolute) if absolute.exists() else None
        dimension_attrs = ""
        if dimensions:
            dimension_attrs = f' width="{dimensions[0]}" height="{dimensions[1]}"'
        alt_attr = html.escape(alt, quote=True)
        common = (
            f'alt="{alt_attr}"{title_attr}{dimension_attrs} loading="lazy" decoding="async" '
            'fetchpriority="low"'
        )

        manifest_entry = self.manifest.get("assets", {}).get(relative, {})
        variants = manifest_entry.get("variants", []) if isinstance(manifest_entry, dict) else []
        webp = [variant for variant in variants if variant.get("format") == "webp"]
        avif = [variant for variant in variants if variant.get("format") == "avif"]
        source_tags: list[str] = []
        for image_type, records in (("image/avif", avif), ("image/webp", webp)):
            if not records:
                continue
            srcset = ", ".join(
                f"/{str(record['path']).lstrip('/')} {int(record['width'])}w"
                for record in sorted(records, key=lambda record: int(record["width"]))
            )
            source_tags.append(
                f'<source type="{image_type}" srcset="{html.escape(srcset, quote=True)}" '
                'sizes="(max-width: 760px) calc(100vw - 64px), min(840px, 72vw)">'
            )

        marker = (
            ' data-specimen="local-truth-charter" data-theme-affinity="museum" '
            'data-load-policy="theme-aware"'
            if is_charter
            else ""
        )
        image = f'<img src="{html.escape(public_src, quote=True)}" {common}>'
        if not source_tags and not is_charter:
            return image
        return (
            f'<picture class="article-media" data-master-src="{html.escape(public_src, quote=True)}"{marker}>'
            + "".join(source_tags)
            + image
            + "</picture>"
        )

    def _is_page_title(self, value: str) -> bool:
        return self._plain_heading(value).casefold() == self.page_title.casefold()

    def _unique_slug(self, value: str) -> str:
        base = re.sub(r"[^a-z0-9\u3400-\u9fff]+", "-", value.lower()).strip("-")[:72] or "section"
        count = self._slug_counts.get(base, 0) + 1
        self._slug_counts[base] = count
        return base if count == 1 else f"{base}-{count}"

    @staticmethod
    def _plain_heading(value: str) -> str:
        value = re.sub(r"`([^`]+)`", r"\1", value)
        value = re.sub(r"!?(?:\[([^\]]*)\])\([^)]*\)", r"\1", value)
        value = re.sub(r"[*_~]", "", value)
        value = re.sub(r"<[^>]+>", "", value)
        return html.unescape(value).strip()


def render_article(root: Path, item: dict) -> tuple[RenderedArticle, dict[str, str], str, dict[str, str], str]:
    source_path = root / item["sourcePath"]
    meta, body, raw_text = read_markdown_document(source_path)
    form = article_form(item, meta, body)
    governance = article_governance(item, meta, item["sourcePath"])
    renderer = MarkdownRenderer(root, source_path, item["title"], load_image_manifest(root))
    rendered = renderer.render(body)
    return rendered, meta, form, governance, content_digest(raw_text)
