#!/usr/bin/env python3
"""Generate responsive WebP/AVIF derivatives for Markdown image masters.

No package install is required.  The generator uses the standards-based canvas
encoder in a locally installed Chromium-family browser, records every output in
a manifest, and always keeps the repository master untouched.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import generate_homepage_data
from article_pipeline import IMAGE_MANIFEST_PATH, image_dimensions


TARGET_WIDTHS = (960, 1440, 2160)
DEFAULT_FORMATS = ("webp", "avif")
MIME_TYPES = {"webp": "image/webp", "avif": "image/avif"}
EXPLICIT_SITE_MASTERS = (
    "resources/pics/QirongZHANG.png",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def discover_markdown_images(root: Path) -> list[Path]:
    images: dict[str, Path] = {}
    for markdown_path in sorted((root / "qrthoughts").rglob("*.md")):
        text = markdown_path.read_text(encoding="utf-8", errors="replace")
        body = generate_homepage_data.markdown_body(text)
        for match in generate_homepage_data.MARKDOWN_IMAGE_RE.finditer(body):
            target = match.group("target").strip("<>")
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, flags=re.I) or target.startswith("//"):
                continue
            candidate = root / target.lstrip("/") if target.startswith("/") else markdown_path.parent / target
            try:
                resolved = candidate.resolve()
                relative = resolved.relative_to(root.resolve()).as_posix()
            except (OSError, ValueError):
                continue
            if resolved.is_file():
                images[relative] = resolved
    for relative in EXPLICIT_SITE_MASTERS:
        resolved = (root / relative).resolve()
        if resolved.is_file():
            images[resolved.relative_to(root.resolve()).as_posix()] = resolved
    return [images[key] for key in sorted(images)]


def find_browser(explicit: str = "") -> Path | None:
    candidates = []
    if explicit:
        candidates.append(explicit)
    for command in ("msedge", "chrome", "chromium", "chromium-browser", "google-chrome"):
        located = shutil.which(command)
        if located:
            candidates.append(located)
    candidates.extend(
        [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
    )
    for candidate in candidates:
        path = Path(candidate)
        if path.is_file():
            return path
    return None


def browser_harness(source: Path, widths: list[int], formats: list[str]) -> str:
    source_uri = source.resolve().as_uri()
    options = {
        "source": source_uri,
        "widths": widths,
        "formats": [MIME_TYPES[fmt] for fmt in formats],
    }
    payload = json.dumps(options, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<meta charset=\"utf-8\">
<pre id=\"result\">{{\"ok\":false,\"error\":\"not-ready\"}}</pre>
<script>
const options = {payload};
const result = document.getElementById('result');
const image = new Image();
image.onload = () => {{
  try {{
    const outputs = [];
    for (const width of options.widths) {{
      const height = Math.max(1, Math.round(image.naturalHeight * width / image.naturalWidth));
      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      const context = canvas.getContext('2d', {{alpha: true}});
      context.imageSmoothingEnabled = true;
      context.imageSmoothingQuality = 'high';
      context.drawImage(image, 0, 0, width, height);
      for (const mime of options.formats) {{
        const dataUrl = canvas.toDataURL(mime, 0.82);
        if (dataUrl.startsWith('data:' + mime + ';base64,')) {{
          outputs.push({{mime, width, height, data: dataUrl.split(',', 2)[1]}});
        }}
      }}
    }}
    result.textContent = JSON.stringify({{ok: true, naturalWidth: image.naturalWidth, naturalHeight: image.naturalHeight, outputs}});
    document.documentElement.dataset.ready = 'true';
  }} catch (error) {{
    result.textContent = JSON.stringify({{ok: false, error: String(error)}});
  }}
}};
image.onerror = () => {{ result.textContent = JSON.stringify({{ok: false, error: 'image-load-failed'}}); }};
image.src = options.source;
</script>
"""


def convert_with_browser(
    browser: Path,
    source: Path,
    widths: list[int],
    formats: list[str],
    timeout_seconds: int = 90,
) -> dict:
    with tempfile.TemporaryDirectory(prefix="zqr-image-") as temp_name:
        temp = Path(temp_name)
        harness = temp / "convert.html"
        harness.write_text(browser_harness(source, widths, formats), encoding="utf-8", newline="\n")
        command = [
            str(browser),
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--allow-file-access-from-files",
            f"--user-data-dir={temp / 'profile'}",
            "--virtual-time-budget=30000",
            "--dump-dom",
            harness.resolve().as_uri(),
        ]
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
        )
        stdout = process.stdout.decode("utf-8", errors="replace")
        match = re.search(r'<pre id="result">([\s\S]*?)</pre>', stdout)
        if not match:
            detail = process.stderr.decode("utf-8", errors="replace")[-1200:]
            raise RuntimeError(f"Browser encoder returned no result for {source.name}: {detail}")
        try:
            result = json.loads(html.unescape(match.group(1)))
        except json.JSONDecodeError as error:
            raise RuntimeError(f"Browser encoder returned invalid JSON for {source.name}") from error
        if not result.get("ok"):
            raise RuntimeError(f"Browser encoder failed for {source.name}: {result.get('error', 'unknown error')}")
        return result


def output_path(root: Path, source_sha: str, width: int, image_format: str) -> Path:
    return root / IMAGE_MANIFEST_PATH.parent / f"{source_sha[:16]}-w{width}.{image_format}"


def generate_derivatives(
    root: Path,
    browser: Path,
    formats: tuple[str, ...] = DEFAULT_FORMATS,
) -> dict:
    root = root.resolve()
    destination = root / IMAGE_MANIFEST_PATH.parent
    destination.mkdir(parents=True, exist_ok=True)
    assets: dict[str, dict] = {}
    unsupported_formats: set[str] = set()

    for source in discover_markdown_images(root):
        relative = source.relative_to(root).as_posix()
        dimensions = image_dimensions(source)
        if not dimensions:
            print(f"SKIP {relative}: unsupported master format", file=sys.stderr)
            continue
        master_width, master_height = dimensions
        widths = [width for width in TARGET_WIDTHS if width <= master_width]
        source_sha = sha256_file(source)
        variants: list[dict] = []
        if widths:
            result = convert_with_browser(browser, source, widths, list(formats))
            returned_formats = {output["mime"].split("/")[-1] for output in result.get("outputs", [])}
            unsupported_formats.update(set(formats) - returned_formats)
            for output in result.get("outputs", []):
                image_format = output["mime"].split("/")[-1]
                if image_format not in formats:
                    continue
                target = output_path(root, source_sha, int(output["width"]), image_format)
                binary = base64.b64decode(output["data"], validate=True)
                target.write_bytes(binary)
                variants.append(
                    {
                        "format": image_format,
                        "width": int(output["width"]),
                        "height": int(output["height"]),
                        "path": target.relative_to(root).as_posix(),
                        "bytes": len(binary),
                        "sha256": hashlib.sha256(binary).hexdigest(),
                    }
                )
                print(f"WROTE {target.relative_to(root).as_posix()} ({len(binary)} bytes)")
        assets[relative] = {
            "masterWidth": master_width,
            "masterHeight": master_height,
            "masterBytes": source.stat().st_size,
            "masterSha256": source_sha,
            "variants": sorted(variants, key=lambda entry: (entry["format"], entry["width"])),
        }

    manifest = {
        "version": 1,
        "generator": "scripts/image_pipeline.py",
        "widths": list(TARGET_WIDTHS),
        "formatsRequested": list(formats),
        "formatsUnsupported": sorted(unsupported_formats),
        "assets": assets,
    }
    manifest_path = root / IMAGE_MANIFEST_PATH
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return manifest


def validate_manifest(root: Path) -> list[str]:
    root = root.resolve()
    manifest_path = root / IMAGE_MANIFEST_PATH
    if not manifest_path.exists():
        return [f"missing manifest: {IMAGE_MANIFEST_PATH.as_posix()}"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [f"invalid manifest JSON: {error}"]
    errors: list[str] = []
    for source_relative, record in manifest.get("assets", {}).items():
        source = root / source_relative
        if not source.exists():
            errors.append(f"missing master: {source_relative}")
            continue
        if sha256_file(source) != record.get("masterSha256"):
            errors.append(f"stale master hash: {source_relative}")
        for variant in record.get("variants", []):
            derivative = root / variant.get("path", "")
            if not derivative.exists():
                errors.append(f"missing derivative: {variant.get('path', '')}")
                continue
            if derivative.stat().st_size != variant.get("bytes"):
                errors.append(f"size mismatch: {variant.get('path', '')}")
            if sha256_file(derivative) != variant.get("sha256"):
                errors.append(f"hash mismatch: {variant.get('path', '')}")
    return errors


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--browser", default="", help="Path to a Chromium-family browser")
    parser.add_argument("--formats", default=",".join(DEFAULT_FORMATS), help="Comma-separated formats")
    parser.add_argument("--check", action="store_true", help="Validate existing files without writing")
    return parser


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = build_arg_parser().parse_args(argv)
    root = Path(args.root)
    if args.check:
        errors = validate_manifest(root)
        if errors:
            for error in errors:
                print("ERROR " + error)
            return 1
        print("Image derivative manifest OK")
        return 0

    formats = tuple(value.strip().lower() for value in args.formats.split(",") if value.strip())
    invalid = [value for value in formats if value not in MIME_TYPES]
    if invalid:
        print("Unsupported requested format(s): " + ", ".join(invalid), file=sys.stderr)
        return 2
    browser = find_browser(args.browser)
    if not browser:
        print("No Chromium-family browser found; cannot encode responsive derivatives.", file=sys.stderr)
        return 2
    manifest = generate_derivatives(root, browser, formats=formats)
    asset_count = len(manifest["assets"])
    variant_count = sum(len(record["variants"]) for record in manifest["assets"].values())
    print(f"Generated manifest for {asset_count} masters and {variant_count} derivatives")
    if manifest["formatsUnsupported"]:
        print("Browser could not encode: " + ", ".join(manifest["formatsUnsupported"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
