#!/usr/bin/env python3
"""Validate registered theme packages, readable content and visual resource budgets."""

from __future__ import annotations

import build_themes
import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT_PAGES = ("index.html", "archive.html", "stats.html", "field.html", "chronicle.html", "series.html")
HOME_BUDGET = 1_500_000


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
    try:
        registry = build_themes.load_registry(root)
    except (ValueError, KeyError, OSError) as exc:
        return [f"theme registry: {exc}"], [], {}
    registry_text = read_text(root / "themes/registry.js")
    payload = re.search(r"window\.ZQR_THEMES\s*=\s*([\s\S]+);\s*$", registry_text)
    if not payload or json.loads(payload.group(1)) != registry:
        errors.append("theme registry.js differs from canonical package metadata; rebuild")
    for relative in ROOT_PAGES:
        path = root / relative
        if not path.exists():
            errors.append(f"missing root surface: {relative}")
            continue
        text = read_text(path)
        if parse_page(path).h1_count != 1:
            errors.append(f"{relative}: expected exactly one h1")
        for fragment in ("themes/registry.js", "includes/js/theme.js", "themes/shared/layout.css"):
            if fragment not in text:
                errors.append(f"{relative}: missing {fragment}")
        if f'data-theme="{registry["default"]}"' not in text:
            errors.append(f"{relative}: default theme differs from registry")
    field_text = read_text(root / "field.html")
    if 'data-charter-object="local-truth"' not in field_text:
        errors.append("field.html: the original charter content must remain accessible")
    system_css = read_text(root / "includes/css/system.css")
    for role in ("--role-displayed", "--role-current", "--role-catalogued", "--role-verified",
                 "--role-gate", "--role-blocked", "--role-simulation", "--role-superseded"):
        if role not in system_css:
            errors.append(f"missing semantic role: {role}")
    layout = read_text(root / "themes/shared/layout.css")
    for marker in ("@media print", "forced-colors", "data-reading", "--reader-font-size"):
        if marker not in layout:
            errors.append(f"shared theme layout missing {marker}")
    for relative in ("index.html", "stats.html", "field.html", "chronicle.html"):
        if "projection-truth.js" not in read_text(root / relative):
            errors.append(f"{relative}: shared freshness calculation is not loaded")
    transfer, assets = field_transfer_bytes(root)
    shared_scene = root / "themes/shared/scene.js"
    largest_preview = 0
    manifest = json.loads(read_text(root / "resources/pics/derivatives/manifest.json"))
    for record in manifest.get("assets", {}).values():
        variants = sorted((v for v in record.get("variants", []) if v.get("format") == "webp"),
                          key=lambda v: v["width"])
        if variants:
            largest_preview = max(largest_preview, variants[0].get("bytes", 0))
        for variant in record.get("variants", []):
            path = root / variant.get("path", "")
            if not path.is_file() or path.stat().st_size != variant.get("bytes"):
                errors.append(f"responsive image derivative missing or drifted: {variant.get('path')}")
    evidence["coreAssets"] = [p.relative_to(root).as_posix() for p in assets if p.is_relative_to(root)]
    evidence["estimateScope"] = "Local bytes: HTML, direct JS/CSS imports, selected package, shared scene, largest preview; not a network or GPU benchmark."
    evidence["themes"] = {}
    for theme in registry["themes"]:
        package_dir = root / "themes" / theme["id"]
        package_bytes = sum(p.stat().st_size for p in package_dir.rglob("*") if p.is_file())
        if package_bytes > theme["maxPackageBytes"]:
            errors.append(f'{theme["id"]}: package exceeds its declared budget')
        estimate = transfer + package_bytes + shared_scene.stat().st_size + largest_preview
        evidence["themes"][theme["id"]] = {"version": theme["version"], "packageBytes": package_bytes,
                                           "estimatedHomeBytes": estimate}
        if estimate > HOME_BUDGET:
            errors.append(f'{theme["id"]}: estimated homepage exceeds {HOME_BUDGET} bytes')
        if theme["colorScheme"] not in ("light", "dark"):
            errors.append(f'{theme["id"]}: invalid colorScheme')
    data = read_text(root / "homepage-data.js")
    if '"summarySource"' not in data or '"narrativeCoverage"' not in data:
        errors.append("homepage truth projection has not been rebuilt")
    if '"curatorial_states"' not in read_text(root / "site-data.js"):
        errors.append("site-plane state contract has not been rebuilt")
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
