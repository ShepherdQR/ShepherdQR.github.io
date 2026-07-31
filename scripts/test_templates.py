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
import validate_site


class HomepageDataTruthTests(unittest.TestCase):
    def narrative_contract(self) -> dict[str, object]:
        reading = "VL-READING-LITERATURE-POETRY"
        engineering = "VL-ENGINEERING-EVIDENCE"
        return {
            "order": [engineering, reading],
            "aliases": {
                engineering.casefold(): engineering,
                reading.casefold(): reading,
                "工程证据": engineering,
                "阅读、文学与诗": reading,
            },
            "series": {"工程证据与发版之后": [engineering]},
            "tags": {"evaluation": [engineering]},
            "selected": {("Thoughts", "0002"): [engineering]},
        }

    def test_excerpt_uses_first_prose_paragraph_only(self) -> None:
        body = """# 标题

副标题
===

```python
print('do not leak')
```

- 结构清单

![图像](/resources/pics/example.png)

| 字段 | 状态 |
| --- | --- |
| T11 | bounded |

https://example.invalid/raw

这是首个 **正文段落**，保留[可读标签](https://example.invalid/link)，移除裸链 https://example.invalid/noise 。

第二段不应进入摘要。
"""
        self.assertEqual(
            generate_homepage_data.markdown_excerpt(body),
            "这是首个 正文段落，保留可读标签，移除裸链 。",
        )

    def test_narrative_mapping_records_provenance_by_priority(self) -> None:
        contract = self.narrative_contract()
        engineering = "VL-ENGINEERING-EVIDENCE"
        reading = "VL-READING-LITERATURE-POETRY"

        explicit = {
            "type": "Books",
            "id": "0001",
            "field_ids": f'["{engineering}"]',
        }
        self.assertEqual(
            generate_homepage_data.resolve_narrative_mapping(explicit, contract, "explicit.md"),
            ([engineering], "frontmatter"),
        )
        with self.assertRaisesRegex(ValueError, "Unknown narrative mapping"):
            generate_homepage_data.resolve_narrative_mapping(
                {"type": "Thoughts", "id": "0099", "field_ids": '["VL-UNKNOWN"]'},
                contract,
                "unknown.md",
            )

        selected = {"type": "Thoughts", "id": "0002"}
        self.assertEqual(
            generate_homepage_data.resolve_narrative_mapping(selected, contract, "selected.md"),
            ([engineering], "selected"),
        )

        taxonomy = {
            "type": "Thoughts",
            "id": "0003",
            "tags": '["evaluation"]',
        }
        self.assertEqual(
            generate_homepage_data.resolve_narrative_mapping(taxonomy, contract, "taxonomy.md"),
            ([engineering], "taxonomy"),
        )

        collection_default = {"type": "Books", "id": "0004"}
        self.assertEqual(
            generate_homepage_data.resolve_narrative_mapping(
                collection_default,
                contract,
                "collection.md",
            ),
            ([reading], "collection_default"),
        )

        unmapped = {"type": "Study", "id": "0005"}
        self.assertEqual(
            generate_homepage_data.resolve_narrative_mapping(unmapped, contract, "unmapped.md"),
            ([], "unmapped"),
        )

    def test_summary_and_narrative_coverage_stats_are_explicit(self) -> None:
        items = [
            {
                "type": "Thoughts",
                "id": "0001",
                "published": "2026-01-02",
                "updatedDate": "2026-01-02",
                "summarySource": "explicit",
                "fieldIds": ["VL-ENGINEERING-EVIDENCE"],
                "mappingSource": "taxonomy",
            },
            {
                "type": "Books",
                "id": "0002",
                "published": "2026-01-01",
                "updatedDate": "2026-01-01",
                "summarySource": "derived",
                "fieldIds": [],
                "mappingSource": "unmapped",
            },
        ]
        payload_text = generate_homepage_data.build_js(items).removeprefix("window.HOMEPAGE_DATA = ").removesuffix(";\n")
        stats = json.loads(payload_text)["stats"]
        self.assertEqual(stats["summaries"], {"explicit": 1, "derived": 1})
        self.assertEqual(stats["narrativeCoverage"]["mapped"], 1)
        self.assertEqual(stats["narrativeCoverage"]["total"], 2)
        self.assertEqual(stats["narrativeCoverage"]["percent"], 50.0)
        self.assertEqual(stats["narrativeCoverage"]["bySource"]["unmapped"], 1)

    def test_featured_and_newest_derived_summaries_are_editorial_warnings(self) -> None:
        items = [
            {"type": "Thoughts", "id": "0001", "summarySource": "derived"},
            {"type": "Thoughts", "id": "0002", "summarySource": "explicit"},
            {"type": "Books", "id": "0003", "summarySource": "derived"},
        ]
        plane = {
            "selected_entries": {
                "items": [{"type": "Books", "id": "0003"}],
            }
        }
        warnings = validate_site.editorial_summary_warnings(items, plane)
        self.assertTrue(any("Thoughts 0001: newest" in warning for warning in warnings))
        self.assertTrue(any("Books 0003: featured/newest" in warning for warning in warnings))
        self.assertFalse(any("Thoughts 0002" in warning for warning in warnings))

    def test_revision_projection_keeps_optional_chain_fields_structured(self) -> None:
        item: dict[str, object] = {}
        generate_homepage_data.project_revision_fields(
            item,
            {
                "revision": "2",
                "revision_status": "superseded",
                "supersedes": '["/thoughts/0001/"]',
                "superseded_by": '["/thoughts/0003/"]',
                "errata": '["typo-001"]',
            },
        )
        self.assertEqual(item["revision"], "2")
        self.assertEqual(item["revisionStatus"], "superseded")
        self.assertEqual(item["supersedes"], ["/thoughts/0001/"])
        self.assertEqual(item["supersededBy"], ["/thoughts/0003/"])
        self.assertEqual(item["errata"], ["typo-001"])

        errors, warnings = validate_site.validate_revision_chains(
            [
                {
                    "type": "Thoughts",
                    "id": "0001",
                    "supersededBy": ["/thoughts/0002/"],
                },
                {
                    "type": "Thoughts",
                    "id": "0002",
                    "supersedes": ["/thoughts/0001/"],
                },
            ]
        )
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_heading_scan_ignores_fenced_examples(self) -> None:
        headings = validate_site.markdown_headings(
            "# Canonical title\n\n```md\n# Example only\n```\n\n### Skipped level"
        )
        self.assertEqual(headings, [(1, "Canonical title", 1), (3, "Skipped level", 7)])


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
