#!/usr/bin/env python3
"""Focused regression tests for build-time article and image durability."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import article_pipeline
import build_site
import generate_homepage_data
import image_pipeline


ROOT = Path(__file__).resolve().parents[1]


class MarkdownDurabilityTests(unittest.TestCase):
    def test_page_title_is_unique_and_body_headings_are_normalized(self) -> None:
        renderer = article_pipeline.MarkdownRenderer(
            ROOT,
            ROOT / "qrthoughts" / "example.md",
            "Canonical title",
        )
        rendered = renderer.render(
            "# Canonical title\n\n# First object\n\n## Detail\n\n# Second object\n"
        )
        self.assertNotIn("<h1", rendered.body_html)
        self.assertIn('<h2 id="first-object">First object</h2>', rendered.body_html)
        self.assertIn('<h3 id="detail">Detail</h3>', rendered.body_html)
        self.assertEqual([heading["level"] for heading in rendered.headings], [2, 3, 2])

    def test_four_article_forms_are_represented(self) -> None:
        items = generate_homepage_data.collect_items(ROOT)
        forms = set()
        for item in items:
            source = ROOT / item["sourcePath"]
            meta, body, _ = article_pipeline.read_markdown_document(source)
            forms.add(article_pipeline.article_form(item, meta, body))
        self.assertEqual(forms, article_pipeline.ARTICLE_FORMS)

    def test_local_truth_charter_survives_static_alias_build(self) -> None:
        item = next(
            item
            for item in generate_homepage_data.collect_items(ROOT)
            if item["type"] == "Thoughts" and item["id"] == "0028"
        )
        alias = ROOT / "thoughts" / "0028" / "index.html"
        page = build_site.build_article_alias_html(item, ROOT, alias)
        self.assertEqual(len(re.findall(r"<h1\b", page, flags=re.I)), 1)
        self.assertIn('data-local-truth-charter="preserved"', page)
        self.assertIn('data-specimen="local-truth-charter"', page)
        self.assertIn('alt="局部真理宪章"', page)
        self.assertIn('"localTruthCharter": "/resources/pics/topos-asi-shadow-luxury-image-v2.png"', page)
        self.assertNotIn("cdn.jsdelivr.net/npm/marked", page)


class ImageDurabilityTests(unittest.TestCase):
    def test_manifest_and_derivative_hashes_are_current(self) -> None:
        self.assertEqual(image_pipeline.validate_manifest(ROOT), [])

    def test_charter_has_all_non_upscaled_webp_widths(self) -> None:
        manifest = article_pipeline.load_image_manifest(ROOT)
        record = manifest["assets"]["resources/pics/topos-asi-shadow-luxury-image-v2.png"]
        widths = {
            variant["width"]
            for variant in record["variants"]
            if variant["format"] == "webp"
        }
        self.assertEqual(widths, {960, 1440, 2160})
        self.assertIn("avif", manifest["formatsUnsupported"])

    def test_homepage_portrait_has_a_non_upscaled_webp(self) -> None:
        manifest = article_pipeline.load_image_manifest(ROOT)
        record = manifest["assets"]["resources/pics/QirongZHANG.png"]
        webp = [variant for variant in record["variants"] if variant["format"] == "webp"]
        self.assertEqual([(variant["width"], variant["height"]) for variant in webp], [(960, 858)])
        self.assertLess(webp[0]["bytes"], record["masterBytes"])


if __name__ == "__main__":
    unittest.main()
