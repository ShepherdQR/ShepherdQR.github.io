#!/usr/bin/env python3
"""Validate generated Markdown article URLs and alias pages."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote, unquote, urlparse
from xml.etree import ElementTree as ET

import generate_homepage_data


DATA_RE = re.compile(r"^\s*window\.HOMEPAGE_DATA\s*=\s*(?P<payload>[\s\S]*?)\s*;\s*$")
SITE_PLANE_RE = re.compile(r"^\s*window\.SITE_PLANE\s*=\s*(?P<payload>[\s\S]*?)\s*;\s*$")
ARTICLE_CONFIG_RE = re.compile(
    r'<script\s+type="application/json"\s+id="article-config"\s*>(?P<payload>[\s\S]*?)</script>',
    re.I,
)
FIELD_RE = re.compile(r"^(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?P<value>.*)$")
FRONT_MATTER_RE = re.compile(
    r"^\ufeff?(?:<!--[\s\S]*?-->\s*)*---\s*\n(?P<yaml>[\s\S]*?)\n---\s*\n"
)
AMBIGUOUS_SETEXT_H2_RE = re.compile(r"(?m)^(?P<text>[^\n#][^\n]*)\n---\s*$")
ATX_H1_RE = re.compile(r"(?m)^#\s+(?P<title>.+?)\s*$")
HTML_REFERENCE_RE = re.compile(r"\b(?:href|src)\s*=\s*['\"](?P<target>[^'\"]+)['\"]", re.I)
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\((?P<target><[^>]+>|[^\s)]+)")
FILE_HEADER_FIELD_RE = re.compile(r"(?m)^\s*- (?P<key>Date|LastEditTime):\s*(?P<value>.+?)\s*$")
ARTICLE_TYPES = {"Books", "Thoughts", "Study", "Videos"}
APPROVED_STATUSES = {"published", "draft", "doing", "archived"}
STATIC_SITEMAP_PATHS = {
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
}
SERIES_STATUSES = {"done", "todo"}
SERIES_MATCH_STATUSES = {"confirmed", "candidate", "unmatched"}
PUBLIC_ROOT_PAGES = {
    "index.html": "https://zqr.world/",
    "archive.html": "https://zqr.world/archive.html",
    "stats.html": "https://zqr.world/stats.html",
    "field.html": "https://zqr.world/field.html",
    "books.html": "https://zqr.world/books.html",
    "thoughts.html": "https://zqr.world/thoughts.html",
    "study.html": "https://zqr.world/study.html",
    "videos.html": "https://zqr.world/videos.html",
    "series.html": "https://zqr.world/series.html",
}
REQUIRED_ITEM_FIELDS = {
    "type",
    "id",
    "title",
    "created",
    "createdDate",
    "published",
    "updated",
    "updatedDate",
    "slug",
    "href",
    "canonicalHref",
    "legacyHref",
    "sourcePath",
    "label",
    "source",
}
REQUIRED_FRONT_MATTER_FIELDS = {
    "type",
    "id",
    "title",
    "created",
    "created_date",
    "published",
    "updated",
    "updated_date",
    "slug",
    "status",
}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return value


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


def validate_markdown_structure(path: Path, root: Path, text: str) -> list[str]:
    """Reject Markdown constructs that are ambiguous in the site's renderer."""
    errors: list[str] = []
    front_matter = FRONT_MATTER_RE.match(text)
    if not front_matter:
        return errors

    body = text[front_matter.end() :]
    rel = path.relative_to(root).as_posix()
    for match in AMBIGUOUS_SETEXT_H2_RE.finditer(body):
        line = text.count("\n", 0, front_matter.end() + match.start()) + 1
        excerpt = match.group("text").strip()
        errors.append(
            f"{rel}:{line}: text followed by --- renders as a level-2 Setext heading; "
            f"use ## for a heading or *** for a divider: {excerpt}"
        )
    return errors


def markdown_source_warnings(path: Path, root: Path, text: str, data: dict[str, str]) -> list[str]:
    warnings: list[str] = []
    front_matter = FRONT_MATTER_RE.match(text)
    if not front_matter:
        return warnings

    rel = path.relative_to(root).as_posix()
    body = text[front_matter.end() :]
    h1_headings = [match.group("title").strip() for match in ATX_H1_RE.finditer(body)]
    if len(h1_headings) > 1:
        warnings.append(
            f"{rel}: body contains {len(h1_headings)} H1 headings; article shell already provides H1: "
            + " | ".join(h1_headings)
        )

    header_fields = {
        match.group("key"): match.group("value").strip()
        for match in FILE_HEADER_FIELD_RE.finditer(text[: front_matter.end()])
    }
    comparisons = [("Date", "created"), ("LastEditTime", "updated")]
    for header_key, front_matter_key in comparisons:
        header_value = header_fields.get(header_key, "")
        front_matter_value = data.get(front_matter_key, "")
        if header_value and front_matter_value and header_value != front_matter_value:
            warnings.append(
                f"{rel}: file header {header_key} differs from front matter {front_matter_key}: "
                f"{header_value} != {front_matter_value}"
            )
    return warnings


def resolve_local_reference(root: Path, source_path: Path, reference: str) -> Path | None:
    reference = html.unescape(reference.strip()).strip("<>")
    if not reference or reference.startswith("#"):
        return None
    parsed = urlparse(reference)
    if parsed.scheme or parsed.netloc or reference.startswith("//"):
        return None
    raw_path = unquote(parsed.path)
    if not raw_path:
        return None
    target = root / raw_path.lstrip("/") if raw_path.startswith("/") else source_path.parent / raw_path
    target = target.resolve()
    if raw_path.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target


def validate_local_html_references(root: Path) -> list[str]:
    errors: list[str] = []
    root_resolved = root.resolve()
    for path in sorted(root.rglob("*.html")):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        for match in HTML_REFERENCE_RE.finditer(read_text(path)):
            reference = match.group("target")
            target = resolve_local_reference(root, path, reference)
            if target is None:
                continue
            try:
                target.relative_to(root_resolved)
            except ValueError:
                errors.append(f"{rel}: local reference escapes repository: {reference}")
                continue
            if not target.exists():
                errors.append(f"{rel}: local reference target does not exist: {reference}")
    return errors


def validate_markdown_images(root: Path) -> list[str]:
    errors: list[str] = []
    root_resolved = root.resolve()
    for path in sorted((root / "qrthoughts").rglob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        rel = path.relative_to(root).as_posix()
        for match in MARKDOWN_IMAGE_RE.finditer(read_text(path)):
            reference = match.group("target")
            target = resolve_local_reference(root, path, reference)
            if target is None:
                continue
            try:
                target.relative_to(root_resolved)
            except ValueError:
                errors.append(f"{rel}: Markdown image escapes repository: {reference}")
                continue
            if not target.exists():
                errors.append(f"{rel}: Markdown image does not exist: {reference}")
    return errors


def load_homepage_data(root: Path) -> dict:
    data_path = root / "homepage-data.js"
    text = read_text(data_path)
    match = DATA_RE.match(text)
    if not match:
        raise ValueError(f"{data_path} does not contain window.HOMEPAGE_DATA JSON")
    return json.loads(match.group("payload"))


def load_site_plane(root: Path) -> dict:
    data_path = root / "site-data.js"
    text = read_text(data_path)
    match = SITE_PLANE_RE.match(text)
    if not match:
        raise ValueError(f"{data_path} does not contain window.SITE_PLANE JSON")
    payload = json.loads(match.group("payload"))
    if not isinstance(payload, dict):
        raise ValueError("site-data.js payload must be an object")
    return payload


def validate_site_plane(root: Path, plane: dict, items: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    source_path = root / "data" / "site-plane.json"
    try:
        source = json.loads(read_text(source_path))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"data/site-plane.json: cannot load public projection: {exc}"]

    if source != plane:
        errors.append("site-data.js: generated projection differs from data/site-plane.json")

    site = plane.get("site") or {}
    governance = plane.get("governance") or {}
    baseline = plane.get("control_plane_baseline") or {}
    operational = baseline.get("operational_frontier") or {}
    candidate = ((baseline.get("evolution_frontier") or {}).get("next_stage_candidate") or {})

    if site.get("owner") != "human":
        errors.append("site-plane: public projection must preserve human ownership")
    if governance.get("control_level") != "L1":
        errors.append("site-plane: control level must remain L1")
    if governance.get("authority_effect") != "none":
        errors.append("site-plane: public projection must not claim an authority effect")
    if candidate.get("status") != "candidate_not_adopted":
        errors.append("site-plane: T12 must remain candidate_not_adopted")
    if candidate.get("adoption_authorized") is not False:
        errors.append("site-plane: T12 adoption must remain unauthorized")

    denied_runtime_flags = {
        "live_watcher_started": operational.get("live_watcher_started"),
        "broker_process_started": operational.get("broker_process_started"),
        "guarded_broker_authorized": operational.get("guarded_broker_authorized"),
        "resident_agent_runtime_started": operational.get("resident_agent_runtime_started"),
        "target_local_adapter_released": operational.get("target_local_adapter_released"),
    }
    for label, value in denied_runtime_flags.items():
        if value is not False:
            errors.append(f"site-plane: {label} must be explicitly false")

    lines = ((plane.get("narrative_lines") or {}).get("items") or [])
    if not isinstance(lines, list) or len(lines) != 5:
        errors.append("site-plane: exactly five public narrative lines are required")
    else:
        line_ids = [line.get("id") for line in lines]
        if len(set(line_ids)) != len(line_ids) or any(not value for value in line_ids):
            errors.append("site-plane: narrative line ids must be present and unique")
        if sum(line.get("weight_hint_percent", 0) for line in lines) != 100:
            errors.append("site-plane: narrative line weights must total 100")

    item_keys = {(item.get("type"), item.get("id")) for item in items}
    selected = ((plane.get("selected_entries") or {}).get("items") or [])
    for entry in selected:
        key = (entry.get("type"), entry.get("id"))
        if key not in item_keys:
            errors.append(f"site-plane: selected entry does not exist: {key[0]} {key[1]}")

    serialized = json.dumps(source, ensure_ascii=False)
    if re.search(r"(?:[A-Za-z]:\\|\\\\)", serialized):
        errors.append("data/site-plane.json: public projection contains an absolute local path")

    visual = plane.get("visual_system") or {}
    profiles = visual.get("profiles") or []
    profile_ids = {profile.get("id") for profile in profiles if isinstance(profile, dict)}
    if profile_ids != {"field", "museum"}:
        errors.append("site-plane: visual system must declare exactly field and museum profiles")
    museum = next((profile for profile in profiles if profile.get("id") == "museum"), {})
    reference = museum.get("canonical_reference", "")
    if not reference or not (root / reference).exists():
        errors.append(f"site-plane: museum canonical reference does not exist: {reference or '<missing>'}")

    thought_28 = next((item for item in items if item.get("type") == "Thoughts" and item.get("id") == "0028"), None)
    if not thought_28 or thought_28.get("leadImage") != "/resources/pics/agi-structure-plan-nine-grid-v2.png":
        errors.append("homepage-data.js: Thoughts 0028 must declare the canonical nine-grid v2 lead image")

    return errors


def validate_public_root_pages(root: Path) -> list[str]:
    errors: list[str] = []
    for rel, canonical in PUBLIC_ROOT_PAGES.items():
        path = root / rel
        if not path.exists():
            errors.append(f"{rel}: public root page is missing")
            continue
        text = read_text(path)
        required_fragments = {
            'meta description': '<meta name="description"',
            'canonical link': f'<link rel="canonical" href="{canonical}"',
            'Atom discovery': 'type="application/atom+xml"',
            'theme controller': 'includes/js/theme.js',
            'skip link': 'class="skip-link"',
            'main target': 'id="main-content"',
        }
        for label, fragment in required_fragments.items():
            if fragment not in text:
                errors.append(f"{rel}: missing {label}")
    return errors


def validate_homepage_scrollability(root: Path) -> list[str]:
    css_path = root / "includes" / "css" / "homepage.css"
    if not css_path.exists():
        return ["includes/css/homepage.css: stylesheet is missing"]

    css = read_text(css_path)
    home_page_rule = re.search(r"\.home-page\s*\{(?P<body>[^}]*)\}", css, re.DOTALL)
    if not home_page_rule:
        return ["includes/css/homepage.css: .home-page rule is missing"]

    declarations = {
        name.strip().lower(): value.strip().lower()
        for name, value in re.findall(r"([\w-]+)\s*:\s*([^;]+);", home_page_rule.group("body"))
    }
    blocked_values = {"hidden", "clip"}
    if declarations.get("overflow") in blocked_values:
        return ["includes/css/homepage.css: .home-page must not block vertical overflow"]
    if declarations.get("overflow-y") in blocked_values:
        return ["includes/css/homepage.css: .home-page must keep vertical scrolling enabled"]
    return []


def alias_path_for(root: Path, item: dict[str, str]) -> Path:
    href = item.get("href", "")
    return root / href.lstrip("/") / "index.html"


def expected_clean_href(item: dict[str, str]) -> str:
    return f"/{item.get('type', '').lower()}/{item.get('id', '')}/"


def expected_legacy_href(item: dict[str, str]) -> str:
    source_path = item.get("sourcePath", "")
    if source_path.lower().endswith(".md"):
        source_path = source_path[:-3]
    return "render.html?md=" + quote("/" + source_path.lstrip("/"), safe="/")


def is_clean_href(href: str) -> bool:
    return bool(re.fullmatch(r"/[a-z]+/\d{4}/", href))


def parse_date(value: str, label: str, errors: list[str], item_label: str) -> dt.date | None:
    if not value:
        return None
    if not DATE_RE.fullmatch(value):
        errors.append(f"{item_label}: {label} is not YYYY-MM-DD: {value}")
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        errors.append(f"{item_label}: {label} is not a valid date: {value}")
        return None


def parse_datetime(value: str, label: str, errors: list[str], item_label: str) -> dt.datetime | None:
    if not value:
        return None
    if DATE_RE.fullmatch(value):
        return dt.datetime.strptime(value, "%Y-%m-%d")
    if not DATETIME_RE.fullmatch(value):
        errors.append(f"{item_label}: {label} is not YYYY-MM-DD or YYYY-MM-DD HH:MM:SS: {value}")
        return None
    try:
        return dt.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        errors.append(f"{item_label}: {label} is not a valid datetime: {value}")
        return None


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

    missing = sorted(field for field in REQUIRED_ITEM_FIELDS if not item.get(field))
    if missing:
        errors.append(f"{label}: missing required item field(s): {', '.join(missing)}")

    href = item.get("href")
    canonical = item.get("canonicalHref")
    legacy = item.get("legacyHref")
    source_path = item.get("sourcePath")

    if item.get("id") and not re.fullmatch(r"\d{4}", item.get("id", "")):
        errors.append(f"{label}: id is not four digits: {item.get('id')}")

    created_date = parse_date(item.get("createdDate", ""), "createdDate", errors, label)
    published = parse_date(item.get("published", ""), "published", errors, label)
    updated_date = parse_date(item.get("updatedDate", ""), "updatedDate", errors, label)
    created = parse_datetime(item.get("created", ""), "created", errors, label)
    updated = parse_datetime(item.get("updated", ""), "updated", errors, label)

    if created and created_date and created.date() != created_date:
        errors.append(f"{label}: created date disagrees with createdDate")
    if updated and updated_date and updated.date() != updated_date:
        errors.append(f"{label}: updated date disagrees with updatedDate")
    if created_date and updated_date and created_date > updated_date:
        errors.append(f"{label}: createdDate is after updatedDate")

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
    elif source_path:
        legacy_md = unquote(urlparse(legacy).query.removeprefix("md="))
        expected_md = "/" + source_path.removesuffix(".md").lstrip("/")
        if legacy_md != expected_md:
            errors.append(f"{label}: legacyHref md does not match sourcePath: {legacy_md} != {expected_md}")
        if legacy != expected_legacy_href(item):
            errors.append(f"{label}: legacyHref is not the canonical sourcePath href: {legacy}")

    if not source_path:
        errors.append(f"{label}: missing sourcePath")
    else:
        md_path = root / source_path.lstrip("/")
        if not md_path.exists():
            errors.append(f"{label}: sourcePath does not exist: {source_path}")
        elif md_path.suffix.lower() != ".md":
            errors.append(f"{label}: sourcePath is not a Markdown file: {source_path}")
        elif f"[{item.get('type')}][{item.get('id')}]" not in md_path.name:
            errors.append(f"{label}: sourcePath filename does not contain matching type/id: {source_path}")

    if item.get("type") not in ARTICLE_TYPES:
        errors.append(f"{label}: unsupported article type for alias page: {item.get('type')}")
        return errors

    if href:
        alias_path = alias_path_for(root, item)
        if not alias_path.exists():
            errors.append(f"{label}: alias page does not exist: {alias_path.relative_to(root).as_posix()}")
        else:
            alias_text = read_text(alias_path)
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
                expected_math = bool(item.get("math"))
                expected_interactive = bool(item.get("interactive"))
                if config.get("math") is not expected_math:
                    errors.append(f"{label}: article-config math flag does not match generated item")
                if config.get("interactive") is not expected_interactive:
                    errors.append(f"{label}: article-config interactive flag does not match generated item")

                has_mathjax = 'id="MathJax-script"' in alias_text
                has_d3 = "includes/js/d3.js" in alias_text
                if has_mathjax != expected_math:
                    errors.append(f"{label}: MathJax dependency presence does not match math flag")
                if has_d3 != expected_interactive:
                    errors.append(f"{label}: D3 dependency presence does not match interactive flag")
                if not re.search(r'<meta\s+name="description"\s+content="[^"]+"', alias_text, re.I):
                    errors.append(f"{label}: generated alias page is missing meta description")

    return errors


def validate_front_matter(root: Path, item: dict[str, str]) -> list[str]:
    errors: list[str] = []
    label = f"{item.get('type', '<missing-type>')} {item.get('id', '<missing-id>')}"
    source_path = item.get("sourcePath", "")
    if not source_path:
        return errors

    md_path = root / source_path.lstrip("/")
    if not md_path.exists():
        return errors

    data = parse_front_matter(read_text(md_path))
    if data is None:
        errors.append(f"{label}: source markdown is missing front matter")
        return errors

    missing = sorted(field for field in REQUIRED_FRONT_MATTER_FIELDS if not data.get(field))
    if missing:
        errors.append(f"{label}: missing required front matter field(s): {', '.join(missing)}")

    status = data.get("status")
    if status and status not in APPROVED_STATUSES:
        errors.append(f"{label}: unsupported front matter status: {status}")
    if status and item.get("source") == "markdown" and status != "published":
        errors.append(f"{label}: homepage markdown item is not published in front matter: {status}")

    field_pairs = [
        ("type", "type"),
        ("id", "id"),
        ("title", "title"),
        ("created", "created"),
        ("created_date", "createdDate"),
        ("published", "published"),
        ("updated", "updated"),
        ("updated_date", "updatedDate"),
        ("slug", "slug"),
    ]
    for front_matter_field, item_field in field_pairs:
        if data.get(front_matter_field) and item.get(item_field) != data.get(front_matter_field):
            errors.append(
                f"{label}: {item_field} differs from front matter {front_matter_field}: "
                f"{item.get(item_field)} != {data.get(front_matter_field)}"
            )

    return errors


def validate_markdown_sources(
    root: Path,
    homepage_keys: set[tuple[str, str]],
) -> tuple[int, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    checked = 0
    for path in sorted((root / "qrthoughts").rglob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        checked += 1
        rel = path.relative_to(root).as_posix()
        text = read_text(path)
        data = parse_front_matter(text)
        if data is None:
            errors.append(f"{rel}: missing front matter")
            continue

        errors.extend(validate_markdown_structure(path, root, text))
        warnings.extend(markdown_source_warnings(path, root, text, data))

        status = data.get("status")
        if status and status not in APPROVED_STATUSES:
            errors.append(f"{rel}: unsupported front matter status: {status}")
        if status == "published":
            missing = sorted(field for field in REQUIRED_FRONT_MATTER_FIELDS if not data.get(field))
            if missing:
                errors.append(f"{rel}: missing required front matter field(s): {', '.join(missing)}")
            key = (data.get("type", ""), data.get("id", ""))
            if key not in homepage_keys:
                errors.append(f"{rel}: published markdown is missing from homepage-data.js")

    return checked, errors, warnings


def validate_uniqueness(items: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    seen: dict[tuple[str, str], int] = {}
    hrefs: dict[str, int] = {}
    source_paths: dict[str, int] = {}
    for index, item in enumerate(items):
        key = (item.get("type", ""), item.get("id", ""))
        if key in seen:
            errors.append(f"{item.get('type')} {item.get('id')}: duplicate type/id with item #{seen[key] + 1}")
        seen[key] = index

        href = item.get("href")
        if href:
            if href in hrefs:
                errors.append(f"{item.get('type')} {item.get('id')}: duplicate href with item #{hrefs[href] + 1}: {href}")
            hrefs[href] = index

        source_path = item.get("sourcePath")
        if source_path:
            if source_path in source_paths:
                errors.append(
                    f"{item.get('type')} {item.get('id')}: duplicate sourcePath with item "
                    f"#{source_paths[source_path] + 1}: {source_path}"
                )
            source_paths[source_path] = index
    return errors


def validate_item_order(items: list[dict[str, str]]) -> list[str]:
    expected = sorted(items, key=generate_homepage_data.item_sort_key, reverse=True)
    actual_keys = [(item.get("type", ""), item.get("id", "")) for item in items]
    expected_keys = [(item.get("type", ""), item.get("id", "")) for item in expected]
    if actual_keys == expected_keys:
        return []

    for index, (actual, expected_key) in enumerate(zip(actual_keys, expected_keys), start=1):
        if actual != expected_key:
            return [
                "homepage-data.js: items are not sorted newest-first; "
                f"position {index} has {actual[0]} {actual[1]}, expected {expected_key[0]} {expected_key[1]}"
            ]
    return ["homepage-data.js: items are not sorted newest-first"]


def validate_stats_and_counts(root: Path, data: dict, items: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    stats = data.get("stats")
    if not isinstance(stats, dict):
        return ["homepage-data.js: missing stats object"]

    by_type: dict[str, int] = {}
    years: dict[str, int] = {}
    for item in items:
        item_type = item.get("type", "")
        published = item.get("published", "")
        by_type[item_type] = by_type.get(item_type, 0) + 1
        if DATE_RE.fullmatch(published):
            years[published[:4]] = years.get(published[:4], 0) + 1

    if stats.get("total") != len(items):
        errors.append(f"stats.total does not match items: {stats.get('total')} != {len(items)}")
    if stats.get("byType") != by_type:
        errors.append(f"stats.byType does not match items: {stats.get('byType')} != {by_type}")
    expected_years = dict(sorted(years.items(), reverse=True))
    if stats.get("years") != expected_years:
        errors.append(f"stats.years does not match items: {stats.get('years')} != {expected_years}")

    for article_type in ARTICLE_TYPES:
        page_dir = root / article_type.lower()
        if not page_dir.exists():
            errors.append(f"{article_type}: collection directory does not exist: {page_dir.name}")
            continue
        generated_pages = [
            path for path in page_dir.iterdir()
            if path.is_dir() and re.fullmatch(r"\d{4}", path.name) and (path / "index.html").exists()
        ]
        expected_count = by_type.get(article_type, 0)
        if len(generated_pages) != expected_count:
            errors.append(f"{article_type}: generated page count does not match items: {len(generated_pages)} != {expected_count}")

    return errors


def xml_root(path: Path) -> ET.Element:
    return ET.parse(path).getroot()


def validate_atom_xml(root: Path) -> list[str]:
    errors: list[str] = []
    atom_path = root / "includes" / "atom.xml"
    if not atom_path.exists():
        return ["includes/atom.xml: file does not exist"]

    try:
        atom_root = xml_root(atom_path)
    except ET.ParseError as exc:
        return [f"includes/atom.xml: not parseable XML: {exc}"]
    except OSError as exc:
        return [f"includes/atom.xml: cannot read file: {exc}"]

    if atom_root.tag.lower() == "html" or atom_root.find(".//title") is not None and atom_root.tag.lower() == "html":
        errors.append("includes/atom.xml: parsed as HTML, not Atom XML")
    if atom_root.tag != "{http://www.w3.org/2005/Atom}feed":
        errors.append(f"includes/atom.xml: root is not Atom feed: {atom_root.tag}")
    return errors


def validate_sitemap_xml(root: Path, markdown_items: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    sitemap_path = root / "sitemap.xml"
    if not sitemap_path.exists():
        return ["sitemap.xml: file does not exist"]

    try:
        sitemap_root = xml_root(sitemap_path)
    except ET.ParseError as exc:
        return [f"sitemap.xml: not parseable XML: {exc}"]
    except OSError as exc:
        return [f"sitemap.xml: cannot read file: {exc}"]

    if sitemap_root.tag != "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset":
        errors.append(f"sitemap.xml: root is not sitemap urlset: {sitemap_root.tag}")
        return errors

    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    loc_paths: set[str] = set()
    for loc in sitemap_root.findall(".//sm:loc", namespace):
        if loc.text:
            path = urlparse(loc.text.strip()).path or "/"
            loc_paths.add(path)

    expected_paths = set(STATIC_SITEMAP_PATHS)
    expected_paths.update(item["canonicalHref"] for item in markdown_items if item.get("canonicalHref"))
    missing = sorted(expected_paths - loc_paths)
    if missing:
        preview = ", ".join(missing[:10])
        if len(missing) > 10:
            preview += f", ... {len(missing) - 10} more"
        errors.append(f"sitemap.xml: missing expected URL path(s): {preview}")

    return errors


def local_path_leak(value: str) -> bool:
    return bool(re.search(r"[A-Za-z]:\\", value) or value.startswith("\\\\"))


def series_href_path(root: Path, href: str) -> Path:
    clean = href.strip()
    if clean.endswith("/"):
        return root / clean.lstrip("/") / "index.html"
    return root / clean.lstrip("/")


def validate_series_books(root: Path) -> list[str]:
    errors: list[str] = []
    data_path = root / "data" / "series-books.json"
    if not data_path.exists():
        return ["data/series-books.json: file does not exist"]

    try:
        payload = json.loads(read_text(data_path))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"data/series-books.json: cannot parse JSON: {exc}"]

    series_list = payload.get("series")
    if not isinstance(series_list, list) or not series_list:
        return ["data/series-books.json: series must be a non-empty array"]

    seen_series: set[str] = set()
    for series in series_list:
        slug = series.get("slug", "")
        label = f"series {slug or '<missing-slug>'}"
        if not slug:
            errors.append("data/series-books.json: series is missing slug")
        elif slug in seen_series:
            errors.append(f"{label}: duplicate slug")
        seen_series.add(slug)

        href = series.get("href", "")
        if not href:
            errors.append(f"{label}: missing href")
        elif local_path_leak(href):
            errors.append(f"{label}: href leaks a local path: {href}")
        elif not series_href_path(root, href).exists():
            errors.append(f"{label}: href target does not exist: {href}")

        items = series.get("items")
        if not isinstance(items, list) or not items:
            errors.append(f"{label}: items must be a non-empty array")
            continue

        seen_work_ids: set[str] = set()
        for item in items:
            work_id = item.get("workId", "")
            item_label = f"{label} / {work_id or '<missing-workId>'}"
            if not work_id:
                errors.append(f"{item_label}: missing workId")
            elif work_id in seen_work_ids:
                errors.append(f"{item_label}: duplicate workId")
            seen_work_ids.add(work_id)

            for field in ["displayTitle", "personOrScope", "seriesPart", "status", "matchStatus"]:
                if not item.get(field):
                    errors.append(f"{item_label}: missing {field}")

            status = item.get("status")
            if status and status not in SERIES_STATUSES:
                errors.append(f"{item_label}: unsupported status: {status}")

            match_status = item.get("matchStatus")
            if match_status and match_status not in SERIES_MATCH_STATUSES:
                errors.append(f"{item_label}: unsupported matchStatus: {match_status}")

            href = item.get("href", "")
            if href:
                if local_path_leak(href):
                    errors.append(f"{item_label}: href leaks a local path: {href}")
                elif not series_href_path(root, href).exists():
                    errors.append(f"{item_label}: href target does not exist: {href}")
            elif status == "done":
                errors.append(f"{item_label}: done item is missing href")

            for value in flatten_string_values(item):
                if local_path_leak(value):
                    errors.append(f"{item_label}: contains local absolute path: {value}")

    return errors


def flatten_string_values(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        strings: list[str] = []
        for item in value:
            strings.extend(flatten_string_values(item))
        return strings
    if isinstance(value, dict):
        strings: list[str] = []
        for item in value.values():
            strings.extend(flatten_string_values(item))
        return strings
    return []


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--max-errors", type=int, default=25, help="Maximum errors to print before truncating.")
    parser.add_argument("--max-warnings", type=int, default=25, help="Maximum warnings to print before truncating.")
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

    try:
        site_plane = load_site_plane(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Site validation failed: cannot load site-data.js: {exc}")
        return 1

    items = data.get("items")
    if not isinstance(items, list):
        print("Site validation failed: homepage-data.js has no items array")
        return 1

    markdown_items = [item for item in items if item.get("source") == "markdown"]
    homepage_keys = {(item.get("type", ""), item.get("id", "")) for item in markdown_items}
    errors: list[str] = []
    errors.extend(validate_uniqueness(items))
    errors.extend(validate_item_order(items))
    errors.extend(validate_stats_and_counts(root, data, items))
    errors.extend(validate_site_plane(root, site_plane, items))
    errors.extend(validate_public_root_pages(root))
    errors.extend(validate_homepage_scrollability(root))
    errors.extend(validate_atom_xml(root))
    errors.extend(validate_sitemap_xml(root, markdown_items))
    errors.extend(validate_series_books(root))
    errors.extend(validate_local_html_references(root))
    errors.extend(validate_markdown_images(root))
    for item in markdown_items:
        errors.extend(validate_item(root, item))
        errors.extend(validate_front_matter(root, item))
    markdown_source_count, markdown_source_errors, warnings = validate_markdown_sources(root, homepage_keys)
    errors.extend(markdown_source_errors)

    print("Site validation summary")
    print(f"  homepage items: {len(items)}")
    print(f"  markdown items checked: {len(markdown_items)}")
    print(f"  markdown sources checked: {markdown_source_count}")
    print(f"  warnings: {len(warnings)}")
    print(f"  errors: {len(errors)}")

    if warnings:
        print()
        print("Warnings:")
        for warning in warnings[: args.max_warnings]:
            print(f"  - {warning}")
        remaining = len(warnings) - args.max_warnings
        if remaining > 0:
            print(f"  ... {remaining} more warning(s) not shown")

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
