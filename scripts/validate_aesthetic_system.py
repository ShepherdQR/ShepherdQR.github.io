#!/usr/bin/env python3
"""Validate the site's institutional visual and material non-regression contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT_PAGES = ("index.html", "archive.html", "stats.html", "field.html", "chronicle.html", "series.html")
FIELD_BUDGET = 1_500_000
MUSEUM_BUDGET = 3_000_000
MUSEUM_LABEL = "局部真理宪章"


class PageInventory(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.h1_count = 0
        self.scripts: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.sources: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if tag == "h1":
            self.h1_count += 1
        elif tag == "script" and data.get("src"):
            self.scripts.append(data)
        elif tag == "link" and data.get("href"):
            self.links.append(data)
        elif tag == "img":
            self.images.append(data)
        elif tag == "source":
            self.sources.append(data)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def local_asset(root: Path, page: Path, value: str) -> Path | None:
    if not value or value.startswith(("data:", "#", "mailto:", "javascript:")):
        return None
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        return None
    relative = parsed.path
    if not relative:
        return None
    if relative.startswith("/"):
        return root / relative.lstrip("/")
    return page.parent / relative


def parse_page(path: Path) -> PageInventory:
    inventory = PageInventory()
    inventory.feed(read_text(path))
    return inventory


def css_dependencies(root: Path, css_path: Path, seen: set[Path] | None = None) -> set[Path]:
    seen = seen or set()
    css_path = css_path.resolve()
    if css_path in seen or not css_path.exists():
        return seen
    seen.add(css_path)
    text = read_text(css_path)
    for value in re.findall(r"@import\s+(?:url\()?['\"]?([^'\")\s]+)", text, flags=re.I):
        dependency = local_asset(root, css_path, value)
        if dependency and dependency.suffix.lower() == ".css":
            css_dependencies(root, dependency, seen)
    return seen


def field_transfer_bytes(root: Path) -> tuple[int, list[Path]]:
    page = root / "index.html"
    inventory = parse_page(page)
    assets: set[Path] = {page.resolve()}
    for script in inventory.scripts:
        if asset := local_asset(root, page, script.get("src", "")):
            assets.add(asset.resolve())
    for link in inventory.links:
        rel = set(link.get("rel", "").split())
        if not rel.intersection({"stylesheet", "icon", "shortcut"}):
            continue
        if asset := local_asset(root, page, link.get("href", "")):
            if asset.suffix.lower() == ".css":
                assets.update(css_dependencies(root, asset))
            else:
                assets.add(asset.resolve())
    for image in inventory.images:
        if image.get("loading") == "lazy" or not image.get("src"):
            continue
        if asset := local_asset(root, page, image["src"]):
            assets.add(asset.resolve())
    existing = [asset for asset in assets if asset.exists()]
    return sum(asset.stat().st_size for asset in existing), sorted(existing)


def check(root: Path) -> tuple[list[str], list[str], dict[str, object]]:
    errors: list[str] = []
    warnings: list[str] = []
    evidence: dict[str, object] = {}

    for relative in ROOT_PAGES:
        path = root / relative
        if not path.exists():
            errors.append(f"missing root surface: {relative}")
            continue
        h1_count = parse_page(path).h1_count
        if h1_count != 1:
            errors.append(f"{relative}: expected exactly one h1, found {h1_count}")

    index_text = read_text(root / "index.html")
    field_text = read_text(root / "field.html")
    theme_text = read_text(root / "includes/js/theme.js")
    homepage_css = read_text(root / "includes/css/homepage.css")
    system_css = read_text(root / "includes/css/system.css")

    if MUSEUM_LABEL not in index_text or 'data-profile-object="museum"' not in index_text:
        errors.append("index.html: Museum Local Truth Charter core exhibit is missing")
    if MUSEUM_LABEL not in field_text or 'data-charter-object="local-truth"' not in field_text:
        errors.append("field.html: System Local Truth Charter object is missing")
    museum_img = re.search(r'<img\b(?=[^>]*data-museum-src=)[^>]*>', index_text, flags=re.I)
    if not museum_img:
        errors.append("index.html: Museum exhibit has no theme-aware image source")
    elif re.search(r'\ssrc\s*=', museum_img.group(0), flags=re.I):
        errors.append("index.html: Field profile eagerly loads the Museum-only exhibit")
    if "hydrateMuseumObjects" not in theme_text or "data-museum-src" not in theme_text:
        errors.append("theme.js: Museum material hydration is missing")
    if not re.search(r'html\[data-theme="museum"\]\s+\.museum-specimen', homepage_css):
        errors.append("homepage.css: Museum exhibit visibility rule is missing")

    required_roles = (
        "--role-displayed",
        "--role-current",
        "--role-catalogued",
        "--role-verified",
        "--role-gate",
        "--role-blocked",
        "--role-simulation",
        "--role-superseded",
    )
    for role in required_roles:
        if role not in system_css:
            errors.append(f"system.css: missing semantic token {role}")

    for relative in ("index.html", "stats.html", "field.html", "chronicle.html"):
        text = read_text(root / relative)
        if "projection-truth.js" not in text:
            errors.append(f"{relative}: shared freshness calculation is not loaded")

    transfer, assets = field_transfer_bytes(root)
    evidence["fieldTransferBytes"] = transfer
    evidence["fieldAssets"] = [asset.relative_to(root).as_posix() for asset in assets if asset.is_relative_to(root)]
    if transfer > FIELD_BUDGET:
        errors.append(f"Field homepage initial transfer {transfer} exceeds {FIELD_BUDGET} bytes")

    manifest_path = root / "resources/pics/derivatives/manifest.json"
    if not manifest_path.exists():
        errors.append("responsive image derivative manifest is missing")
    else:
        manifest = json.loads(read_text(manifest_path))
        charter = (manifest.get("assets") or {}).get("resources/pics/topos-asi-shadow-luxury-image-v2.png")
        variants = (charter or {}).get("variants") or []
        widths = {variant.get("width") for variant in variants if variant.get("format") == "webp"}
        if not {960, 1440, 2160}.issubset(widths):
            errors.append("Local Truth Charter is missing 960/1440/2160 WebP derivatives")
        portrait = (manifest.get("assets") or {}).get("resources/pics/QirongZHANG.png")
        portrait_widths = {
            variant.get("width") for variant in (portrait or {}).get("variants") or []
            if variant.get("format") == "webp"
        }
        if 960 not in portrait_widths:
            errors.append("Homepage portrait is missing its 960px WebP derivative")
        museum_variant = next((variant for variant in variants if variant.get("width") == 1440 and variant.get("format") == "webp"), None)
        museum_transfer = transfer + int((museum_variant or {}).get("bytes") or 0)
        evidence["museumTransferBytes"] = museum_transfer
        evidence["imageFormatsUnsupported"] = manifest.get("formatsUnsupported") or []
        if museum_transfer > MUSEUM_BUDGET:
            errors.append(f"Museum homepage initial transfer {museum_transfer} exceeds {MUSEUM_BUDGET} bytes")
        for asset_name, record in (manifest.get("assets") or {}).items():
            for variant in record.get("variants") or []:
                variant_path = root / variant.get("path", "")
                if not variant_path.exists():
                    errors.append(f"missing responsive derivative: {variant.get('path')}")
                elif variant_path.stat().st_size != variant.get("bytes"):
                    errors.append(f"derivative byte count drift: {variant.get('path')}")

    homepage_data = read_text(root / "homepage-data.js")
    if '"summarySource"' not in homepage_data or '"narrativeCoverage"' not in homepage_data:
        errors.append("homepage-data.js: truth projection has not been rebuilt")
    if '"curatorial_states"' not in read_text(root / "site-data.js"):
        errors.append("site-data.js: curatorial state contract has not been rebuilt")

    if "field_ids" not in read_text(root / "scripts/new_note.py"):
        errors.append("new_note.py: authoring template does not expose narrative mapping")

    return errors, warnings, evidence


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    errors, warnings, evidence = check(root)
    print("Aesthetic system validation")
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    print(f"Result: {'OK' if not errors else 'FAILED'} ({len(errors)} errors, {len(warnings)} warnings)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
