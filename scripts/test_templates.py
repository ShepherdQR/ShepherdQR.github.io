#!/usr/bin/env python3
"""Regression checks for the canonical note source and article shell templates."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import build_site
import generate_homepage_data
import new_note


class NewNoteTemplateTests(unittest.TestCase):
    def render(self, **overrides: object) -> str:
        values: dict[str, object] = {
            "content_type": "Thoughts",
            "content_id": "0042",
            "title": "结构化新笔记",
            "now": "2026-07-15 10:30:00",
            "date": "2026-07-15",
            "status": "published",
            "tags": ["agent", "evidence"],
            "series": "约束场与复杂智能",
            "summary": "验证当前作者模板和公共文章模板保持一致。",
            "lead_image": "/resources/pics/example.png",
            "math_enabled": True,
            "interactive_enabled": True,
        }
        values.update(overrides)
        return new_note.build_markdown(**values)  # type: ignore[arg-type]

    def test_rich_metadata_contract_is_emitted(self) -> None:
        text = self.render()
        data = generate_homepage_data.parse_front_matter(text)
        self.assertIsNotNone(data)
        assert data is not None
        self.assertEqual(data["summary"], "验证当前作者模板和公共文章模板保持一致。")
        self.assertEqual(generate_homepage_data.parse_list(data["tags"]), ["agent", "evidence"])
        self.assertEqual(data["series"], "约束场与复杂智能")
        self.assertEqual(data["lead_image"], "/resources/pics/example.png")
        self.assertTrue(generate_homepage_data.parse_bool(data["math"]))
        self.assertTrue(generate_homepage_data.parse_bool(data["interactive"]))
        self.assertTrue(text.startswith("<!---------------------------------------------------------"))
        self.assertTrue(generate_homepage_data.markdown_body(text).startswith("# 结构化新笔记"))

    def test_optional_fields_keep_a_stable_shape(self) -> None:
        text = self.render(
            tags=[],
            series=None,
            summary=None,
            lead_image=None,
            math_enabled=False,
            interactive_enabled=False,
        )
        data = generate_homepage_data.parse_front_matter(text)
        self.assertIsNotNone(data)
        assert data is not None
        for field in ("summary", "tags", "series", "lead_image", "math", "interactive"):
            self.assertIn(field, data)
        self.assertEqual(generate_homepage_data.parse_list(data["tags"]), [])
        self.assertFalse(generate_homepage_data.parse_bool(data["math"]))
        self.assertFalse(generate_homepage_data.parse_bool(data["interactive"]))


class ArticleTemplateTests(unittest.TestCase):
    def test_generated_article_uses_current_knowledge_interface(self) -> None:
        root = Path("repo")
        alias_path = root / "thoughts" / "0042" / "index.html"
        item = {
            "title": "结构化新笔记",
            "summary": "验证公共文章模板。",
            "canonicalHref": "/thoughts/0042/",
            "sourcePath": "qrthoughts/year2026/month7/[Thoughts][0042][结构化新笔记].md",
        }
        rendered = build_site.build_article_alias_html(item, root, alias_path)
        for fragment in (
            '<html lang="zh-CN" data-theme="field">',
            f'data-template="{build_site.ARTICLE_TEMPLATE_VERSION}"',
            'class="skip-link"',
            'id="main-content"',
            ">Field</a>",
            ">Atlas</a>",
            ">Evidence</a>",
            ">System</a>",
            ">Series</a>",
            "includes/js/theme.js",
        ):
            self.assertIn(fragment, rendered)

        config_match = re.search(
            r'<script type="application/json" id="article-config">(?P<payload>[\s\S]*?)</script>',
            rendered,
        )
        self.assertIsNotNone(config_match)
        assert config_match is not None
        config = json.loads(config_match.group("payload"))
        self.assertEqual(config["template"], build_site.ARTICLE_TEMPLATE_VERSION)


if __name__ == "__main__":
    unittest.main()
