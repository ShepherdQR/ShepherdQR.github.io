#!/usr/bin/env python3
"""Build durable reading-series data and Markdown registers from source snapshots.

The normal site build remains offline. This maintenance helper is run only when
refreshing the two large catalogs and consumes snapshots downloaded separately
from the authoritative source URLs recorded below.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import unicodedata
from html.parser import HTMLParser
from pathlib import Path


COMMERCIAL_PRESS_CATALOG_URL = "https://www.cp.com.cn/Content/2024/09-24/1114372535.html"
COMMERCIAL_PRESS_COLOR_URL = "https://www.cp.com.cn/book/5ba19583-9.html"
COMMERCIAL_PRESS_CURRENT_SCOPE_URL = "https://www.cp.com.cn/Content/2025/09-16/1530565240.html"
NOBEL_API_URL = (
    "https://api.nobelprize.org/2.1/nobelPrizes"
    "?nobelPrizeCategory=lit&limit=200&sort=asc"
)
NOBEL_LAUREATES_API_URL = (
    "https://api.nobelprize.org/2.1/laureates"
    "?nobelPrizeCategory=lit&limit=200&sort=asc"
)
WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"


HANYI_CATEGORIES = {
    "哲学": {
        "code": "PH",
        "label": "橙色 · 哲学",
        "color": "orange",
        "description": "哲学、宗教、逻辑、科学哲学与思想史",
    },
    "政治学·法学·社会学·教育学": {
        "code": "PLS",
        "label": "绿色 · 政治·法律·社会",
        "color": "green",
        "description": "政治学、法学、社会学、人类学与教育学",
    },
    "历史学·地理学": {
        "code": "HG",
        "label": "黄色 · 历史·地理",
        "color": "yellow",
        "description": "历史学、史学理论、文明史与地理学",
    },
    "经济学·管理学": {
        "code": "EM",
        "label": "蓝色 · 经济·管理",
        "color": "blue",
        "description": "经济学、经济史、财政金融与管理学",
    },
    "语言学·文学艺术理论": {
        "code": "LA",
        "label": "赭色 · 语言·文学艺术理论",
        "color": "umber",
        "description": "语言学、文学理论、美学与艺术史",
    },
}


# Confirmed public notes for titles in the official 1000-title baseline.
HANYI_NOTE_MATCHES = {
    "对笛卡尔《沉思》的诘难": "0016",
    "人是机器": "0009",
    "袖珍神学": "0078",
    "科学中华而不实的作风": "0030",
    "一年有半、续一年有半": "0064",
    "劝学篇": "0031",
    "范畴篇解释篇": "0077",
    "知性改进论": "0010",
    "自然哲学": "0029",
    "人生的亲证": "0075",
    "泛神论要义": "0006",
    "面向思的事情": "0054",
    "谈谈方法": "0025",
    "算术基础": "0049",
    "计算机与人脑": "0008",
    "卡布斯教诲录": "0018",
    "乌托邦": "0107",
    "人类幸福论": "0116",
    "民族主义": "0115",
    "论出版自由": "0111",
}

# The official baseline contains two different books titled 《自然哲学》.
# The public note and local filename identify the one authored by Schlick.
HANYI_AUTHOR_GUARDS = {"自然哲学": "石里克"}


# Site notes are evidence of reading at least one work by the laureate. The
# 1949 and 1980 mappings stay candidates for the reasons recorded here.
NOBEL_NOTE_MATCHES = {
    "1901": {"noteId": "0038"},
    "1907": {"noteId": "0044"},
    "1911": {"noteId": "0058"},
    "1913": {"noteId": "0051"},
    "1923": {"noteId": "0057"},
    "1925": {"noteId": "0066"},
    "1948": {"noteId": "0095"},
    "1949": {
        "noteId": "0117",
        "candidate": True,
        "annotation": "站内福克纳笔记标题写作 1994；官方获奖年份为 1949，保留为候选匹配。",
    },
    "1954": {"noteId": "0042"},
    "1956": {"noteId": "0059"},
    "1957": {"noteId": "0043"},
    "1968": {"noteId": "0083"},
    "1969": {"noteId": "0085"},
    "1972": {"noteId": "0060"},
    "1980": {
        "noteId": "0023",
        "candidate": True,
        "annotation": "站内《切·米沃什诗选》未以诺奖为题名，但可作为该得主的候选阅读记录。",
    },
    "1982": {"noteId": "0092"},
    "1996": {"noteId": "0112"},
    "2003": {"noteId": "0061"},
    "2011": {"noteId": "0082"},
    "2012": {"noteId": "0036"},
    "2022": {"noteId": "0053"},
    "2024": {"noteId": "0119"},
}


HANYI_PRIORITY_TITLES = [
    "理想国",
    "尼各马可伦理学",
    "人性论",
    "纯粹理性批判",
    "实践理性批判",
    "存在与时间",
    "逻辑哲学论",
    "科学哲学的兴起",
    "政治学",
    "社会契约论",
    "论法的精神(上下卷)",
    "利维坦",
    "政府论（上下篇）",
    "论自由",
    "道德与立法原理导论",
    "旧制度与大革命",
    "宗教与资本主义的兴起",
    "社会学方法的准则",
    "国民财富的性质和原因的研究（上下卷）",
    "就业、利息和货币通论（重译本）",
    "经济发展理论",
    "资本主义与自由",
    "希罗多德历史(上下册)",
    "伯罗奔尼撒战争史(上下册)",
    "罗马帝国衰亡史(上下册)",
    "历史是什么？",
    "封建社会(上下册)",
    "普通语言学教程",
    "语言论：言语研究导论",
    "小说理论",
    "摹仿论",
    "艺术即经验",
]


class CommercialPressCatalogParser(HTMLParser):
    """Extract the five catalog tables from the official HTML page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.current_category: str | None = None
        self.in_strong = False
        self.strong_text: list[str] = []
        self.in_tr = False
        self.in_td = False
        self.cell_text: list[str] = []
        self.row: list[str] = []
        self.books: dict[str, list[dict[str, str | int]]] = {
            category: [] for category in HANYI_CATEGORIES
        }

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "strong":
            self.in_strong = True
            self.strong_text = []
        elif tag == "tr":
            self.in_tr = True
            self.row = []
        elif tag == "td" and self.in_tr:
            self.in_td = True
            self.cell_text = []

    def handle_data(self, data: str) -> None:
        if self.in_strong:
            self.strong_text.append(data)
        if self.in_td:
            self.cell_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "strong" and self.in_strong:
            label = compact_text("".join(self.strong_text))
            if label in HANYI_CATEGORIES:
                self.current_category = label
            self.in_strong = False
        elif tag == "td" and self.in_td:
            self.row.append(compact_text("".join(self.cell_text)))
            self.in_td = False
        elif tag == "tr" and self.in_tr:
            self._finish_row()
            self.in_tr = False

    def _finish_row(self) -> None:
        if self.current_category is None or len(self.row) < 2:
            return
        match = re.match(r"^(\d+)[.．、]\s*(.+)$", self.row[0])
        if not match:
            return
        self.books[self.current_category].append(
            {
                "catalogIndex": int(match.group(1)),
                "title": compact_text(match.group(2)),
                "author": compact_text(self.row[1]),
            }
        )


def compact_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value).replace("\xa0", " ")).strip()


def normalize_title(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = value.replace("徳", "德")
    return re.sub(r"[\s·•—–\-_:：,，.。、《》〈〉“”‘’'\"()（）\[\]【】、？?]", "", value).lower()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def note_index(root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    pattern = re.compile(r"^\[Books\]\[(\d{4})\]")
    for path in sorted((root / "qrthoughts").rglob("*.md")):
        match = pattern.match(path.name)
        if match:
            result[match.group(1)] = path
    return result


def public_note_source(path: Path) -> str:
    return path.stem


def parse_hanyi_catalog(path: Path) -> dict[str, list[dict[str, str | int]]]:
    parser = CommercialPressCatalogParser()
    parser.feed(path.read_text(encoding="utf-8"))
    counts = {category: len(items) for category, items in parser.books.items()}
    total = sum(counts.values())
    if total != 1000:
        raise ValueError(f"Expected 1000 official catalog titles, found {total}: {counts}")
    for category, items in parser.books.items():
        expected = list(range(1, len(items) + 1))
        actual = [int(item["catalogIndex"]) for item in items]
        if actual != expected:
            raise ValueError(f"Non-contiguous official order in {category}")
    return parser.books


def hanyi_series(
    catalog: dict[str, list[dict[str, str | int]]],
    notes: dict[str, Path],
    as_of: str,
) -> dict:
    normalized_matches = {normalize_title(title): note_id for title, note_id in HANYI_NOTE_MATCHES.items()}
    seen_matches: set[str] = set()
    items: list[dict] = []
    sequence = 0

    for category, config in HANYI_CATEGORIES.items():
        for record in catalog[category]:
            sequence += 1
            title = str(record["title"])
            note_id = normalized_matches.get(normalize_title(title))
            author_guard = HANYI_AUTHOR_GUARDS.get(title)
            if note_id and author_guard and author_guard not in str(record["author"]):
                note_id = None
            status = "done" if note_id else "todo"
            item = {
                "workId": f"hanyi-{config['code'].lower()}-{int(record['catalogIndex']):04d}",
                "displayTitle": title,
                "personOrScope": str(record["author"]) or "作者信息未列",
                "kind": "book",
                "seriesPart": config["label"],
                "groupColor": config["color"],
                "status": status,
                "matchStatus": "confirmed" if note_id else "unmatched",
                "sequence": sequence,
                "catalogIndex": int(record["catalogIndex"]),
                "catalogCode": f"HY-{config['code']}-{int(record['catalogIndex']):03d}",
                "sourceLabels": ["商务印书馆1000种书目"],
                "sourceUrl": COMMERCIAL_PRESS_CATALOG_URL,
            }
            if note_id:
                if note_id not in notes:
                    raise ValueError(f"Hanyi note {note_id} does not exist")
                item.update(
                    {
                        "href": f"/books/{note_id}/",
                        "noteId": note_id,
                        "sourceLabels": ["商务印书馆1000种书目", "site-md", "local-done"],
                        "sourceNames": [public_note_source(notes[note_id])],
                    }
                )
                seen_matches.add(note_id)
            items.append(item)

    expected_matches = set(HANYI_NOTE_MATCHES.values())
    missing = sorted(expected_matches - seen_matches)
    if missing:
        raise ValueError(f"Hanyi notes were not matched to official titles: {missing}")

    groups = [
        {
            "label": config["label"],
            "color": config["color"],
            "description": config["description"],
        }
        for config in HANYI_CATEGORIES.values()
    ]
    return {
        "slug": "hanyi-world-academic-classics",
        "title": "[汉译世界学术名著丛书]",
        "displayTitle": "汉译世界学术名著丛书",
        "description": "按商务印书馆五色学科体系整理的 1000 种基线书目、站内已读记录与未读路径。",
        "href": "/series/hanyi-world-academic-classics/",
        "readingListHref": "/reading-lists/hanyi-world-academic-classics-unread.md",
        "readingListLabel": "未读书目 MD",
        "tags": ["Academic classics", "Translation", "Commercial Press", "1000-title baseline"],
        "lastUpdated": as_of,
        "groupLabel": "颜色 / 学科",
        "groupOrder": [group["label"] for group in groups],
        "groups": groups,
        "unitLabel": "titles",
        "defaultSort": "series",
        "defaultView": "catalog",
        "sortLabels": {"series": "按官方书目", "person": "按作者", "note": "按阅读页"},
        "pageSize": 80,
        "sourceSummary": {
            "officialBaseline": 1000,
            "siteDoneWorks": sum(item["status"] == "done" for item in items),
            "todoWorks": sum(item["status"] == "todo" for item in items),
            "colorGroups": 5,
        },
        "scopeNote": "完整可复核基线为商务印书馆 2024 年发布的 1000 种书目；2025 年官方称前 23 辑已超过 1000 种。",
        "sources": [
            {
                "url": COMMERCIAL_PRESS_CATALOG_URL,
                "date": "2024-09-24",
                "usedFor": "1000 种完整书名、作者与五大学科分组",
                "confidence": "high",
            },
            {
                "url": COMMERCIAL_PRESS_COLOR_URL,
                "date": "2017",
                "usedFor": "橙、绿、蓝、黄、赭五色与学科映射",
                "confidence": "high",
            },
            {
                "url": COMMERCIAL_PRESS_CURRENT_SCOPE_URL,
                "date": "2025-09-16",
                "usedFor": "前 23 辑规模已超过 1000 种的边界说明",
                "confidence": "high",
            },
        ],
        "items": items,
    }


def decade_group(year: str) -> str:
    value = int(year)
    if value <= 1929:
        return "1901–1929"
    if value <= 1959:
        return "1930–1959"
    if value <= 1989:
        return "1960–1989"
    if value <= 2019:
        return "1990–2019"
    return "2020–2025"


def label_value(labels: dict, language: str) -> str:
    entry = labels.get(language)
    if isinstance(entry, dict):
        return str(entry.get("value", ""))
    return ""


def nobel_series(
    prizes_payload: dict,
    laureates_payload: dict,
    wikidata_labels: dict,
    notes: dict[str, Path],
    as_of: str,
) -> dict:
    laureate_details = {str(item["id"]): item for item in laureates_payload["laureates"]}
    items: list[dict] = []
    awarded_prizes = 0
    no_award_years: list[str] = []
    seen_note_ids: set[str] = set()

    for prize in prizes_payload["nobelPrizes"]:
        year = str(prize["awardYear"])
        laureates = prize.get("laureates") or []
        if not laureates:
            no_award_years.append(year)
            continue
        awarded_prizes += 1
        for laureate in laureates:
            laureate_id = str(laureate["id"])
            detail = laureate_details[laureate_id]
            official_name = laureate.get("knownName", laureate.get("fullName", {})).get("en", laureate_id)
            wikidata_id = detail.get("wikidata", {}).get("id", "")
            labels = wikidata_labels.get(wikidata_id, {})
            chinese_name = (
                label_value(labels, "zh-cn")
                or label_value(labels, "zh-hans")
                or label_value(labels, "zh")
                or official_name
            )
            note = NOBEL_NOTE_MATCHES.get(year)
            note_id = note.get("noteId") if note else ""
            status = "done" if note_id else "todo"
            candidate = bool(note and note.get("candidate"))
            source_url = next(
                (
                    link.get("href", "")
                    for award in detail.get("nobelPrizes", [])
                    if award.get("awardYear") == year
                    for link in award.get("links", [])
                    if link.get("rel") == "external" and "facts" in link.get("class", [])
                ),
                f"https://www.nobelprize.org/laureate/{laureate_id}",
            )
            item = {
                "workId": f"nobel-lit-{year}-{laureate_id}",
                "displayTitle": chinese_name,
                "personOrScope": official_name,
                "kind": "laureate",
                "seriesPart": decade_group(year),
                "status": status,
                "matchStatus": "candidate" if candidate else ("confirmed" if note_id else "unmatched"),
                "sequence": int(year) * 10 + int(laureate.get("sortOrder", "1")),
                "awardYear": year,
                "laureateId": laureate_id,
                "sourceLabels": ["NobelPrize.org"],
                "sourceUrl": source_url,
                "sourceNames": [official_name],
            }
            if wikidata_id:
                item["wikidataId"] = wikidata_id
            if note_id:
                if note_id not in notes:
                    raise ValueError(f"Nobel note {note_id} does not exist")
                item.update(
                    {
                        "href": f"/books/{note_id}/",
                        "noteId": note_id,
                        "sourceLabels": ["NobelPrize.org", "site-md"] + (["candidate-note"] if candidate else []),
                        "sourceNames": [official_name, public_note_source(notes[note_id])],
                    }
                )
                if note and note.get("annotation"):
                    item["annotation"] = note["annotation"]
                seen_note_ids.add(note_id)
            items.append(item)

    expected_note_ids = {str(item["noteId"]) for item in NOBEL_NOTE_MATCHES.values()}
    missing = sorted(expected_note_ids - seen_note_ids)
    if missing:
        raise ValueError(f"Nobel notes were not matched: {missing}")
    if len(items) != 122 or awarded_prizes != 118:
        raise ValueError(f"Unexpected Nobel baseline: {awarded_prizes} prizes / {len(items)} laureates")

    group_order = ["1901–1929", "1930–1959", "1960–1989", "1990–2019", "2020–2025"]
    return {
        "slug": "nobel-literature",
        "title": "[诺贝尔文学奖]",
        "displayTitle": "诺贝尔文学奖阅读系列",
        "description": "按官方获奖年份排列 1901—2025 年文学奖得主，并关联站内已读作品。",
        "href": "/series/nobel-literature/",
        "readingListHref": "/reading-lists/nobel-literature-reading-progress.md",
        "readingListLabel": "阅读进度 MD",
        "tags": ["Nobel Prize", "Literature", "1901–2025"],
        "lastUpdated": as_of,
        "groupLabel": "获奖年代",
        "groupOrder": group_order,
        "unitLabel": "laureates",
        "defaultSort": "series",
        "defaultView": "catalog",
        "sortLabels": {"series": "按获奖年份", "person": "按得主姓名", "note": "按阅读页"},
        "pageSize": 80,
        "sourceSummary": {
            "awardedPrizes": awarded_prizes,
            "officialLaureates": len(items),
            "siteDoneLaureates": len(seen_note_ids),
            "todoLaureates": len(items) - len(seen_note_ids),
            "candidateMatches": sum(item["matchStatus"] == "candidate" for item in items),
            "noAwardYears": len(no_award_years),
        },
        "noAwardYears": no_award_years,
        "scopeNote": "一位得主只要已有至少一篇公开作品阅读笔记，即记为 done；这不是其全部作品已读完。",
        "sources": [
            {
                "url": NOBEL_API_URL,
                "date": as_of,
                "usedFor": "1901—2025 年奖项、得主、年份与官方姓名",
                "confidence": "high",
            },
            {
                "url": NOBEL_LAUREATES_API_URL,
                "date": as_of,
                "usedFor": "得主稳定标识与官方详情页",
                "confidence": "high",
            },
            {
                "url": WIKIDATA_API_URL,
                "date": as_of,
                "usedFor": "简体中文显示名；无简体标签时回退官方英文名",
                "confidence": "medium",
            },
        ],
        "items": items,
    }


def write_hanyi_markdown(path: Path, series: dict, as_of: str) -> None:
    items = series["items"]
    by_group = {label: [item for item in items if item["seriesPart"] == label] for label in series["groupOrder"]}
    title_lookup = {normalize_title(item["displayTitle"]): item for item in items}
    priority: list[dict] = []
    missing_priority: list[str] = []
    for title in HANYI_PRIORITY_TITLES:
        item = title_lookup.get(normalize_title(title))
        if item is None:
            missing_priority.append(title)
        elif item["status"] == "todo":
            priority.append(item)
    if missing_priority:
        raise ValueError(f"Priority titles missing from official catalog: {missing_priority}")

    lines = [
        "# 汉译世界学术名著丛书：未读书目",
        "",
        f"生成日期：{as_of}",
        "",
        "范围：以商务印书馆 2024-09-24 公布的 **1000 种完整书目** 为可复核基线，减去本站已有阅读笔记的 20 种；本表因此有 980 个未读项。商务印书馆 2025 年已说明前 23 辑规模超过 1000 种，本文件不把 1000 种基线冒充绝对最新全集。",
        "",
        "状态口径：`[ ]` 仅表示本站尚无公开阅读笔记，不等同于从未翻阅、未收藏或未购买。多卷本按一个品种计。",
        "",
        "## 五色分类",
        "",
        "| 颜色与学科 | 基线 | 已读 | 未读 | 说明 |",
        "|---|---:|---:|---:|---|",
    ]
    for group in series["groups"]:
        group_items = by_group[group["label"]]
        done = sum(item["status"] == "done" for item in group_items)
        lines.append(
            f"| {group['label']} | {len(group_items)} | {done} | {len(group_items) - done} | {group['description']} |"
        )
    lines.extend(
        [
            "",
            "## 建议起读顺序",
            "",
            "这不是对 980 种书的价值排名，而是一条先建立共同概念、再进入专门研究的首轮路径。已读书目自动从本段排除；完整清单仍按官方分科与原表顺序列在后面。",
            "",
        ]
    )
    for index, item in enumerate(priority, 1):
        author = f" — {item['personOrScope']}" if item["personOrScope"] != "作者信息未列" else ""
        lines.append(f"{index}. `{item['catalogCode']}` 《{item['displayTitle']}》{author}（{item['seriesPart']}）")
    lines.extend(["", "## 完整未读清单", ""])
    for group in series["groups"]:
        label = group["label"]
        lines.extend([f"### {label}", "", group["description"] + "。", ""])
        for item in by_group[label]:
            if item["status"] != "todo":
                continue
            author = f" — {item['personOrScope']}" if item["personOrScope"] != "作者信息未列" else ""
            lines.append(f"- [ ] `{item['catalogCode']}` 《{item['displayTitle']}》{author}")
        lines.append("")
    lines.extend(
        [
            "## 来源登记",
            "",
            "| 来源 | 日期 | 用途 | 置信度 |",
            "|---|---:|---|---|",
            f"| [商务印书馆：1000 种书目]({COMMERCIAL_PRESS_CATALOG_URL}) | 2024-09-24 | 完整书名、作者、五大学科分组及组内顺序 | 高 |",
            f"| [商务印书馆：120 年纪念版分科本]({COMMERCIAL_PRESS_COLOR_URL}) | 2017 | 橙、绿、蓝、黄、赭五色对应关系 | 高 |",
            f"| [商务印书馆：第二十四辑论证会]({COMMERCIAL_PRESS_CURRENT_SCOPE_URL}) | 2025-09-16 | 说明前 23 辑已超过 1000 种，限定本表边界 | 高 |",
            "| `qrthoughts/**/*.md` | 当前检出 | 已有公开阅读笔记及 `/books/NNNN/` 链接 | 高 |",
            "| 本地已读库文件名扫描 | 当前检出 | 复核 20 个已读对象；不公开私人文件路径 | 高（文件名） |",
            "",
            "## 维护规则",
            "",
            "1. 新增阅读笔记后，在 `scripts/build_reading_series.py` 的 `HANYI_NOTE_MATCHES` 中登记官方书名与 Books ID。",
            "2. 重新取得官方页面快照后运行脚本；脚本会验证总数、分类顺序、笔记链接和匹配完整性。",
            "3. 若采用超过 1000 种的新官方完整总表，先修改范围说明，再整体更新；不要把零散新品悄悄混入旧基线。",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def write_nobel_markdown(path: Path, series: dict, as_of: str) -> None:
    items = series["items"]
    done = sum(item["status"] == "done" for item in items)
    lines = [
        "# 诺贝尔文学奖：阅读进度",
        "",
        f"生成日期：{as_of}",
        "",
        f"范围：诺贝尔奖官方 API 中 1901—2025 年的 118 次文学奖、122 位得主。当前关联 {done} 位得主的站内阅读记录；一位得主有一篇作品笔记即记为已读入口，不代表其作品全集已经读完。",
        "",
        f"未颁奖年份：{', '.join(series['noAwardYears'])}。",
        "",
        "## 时间序列",
        "",
    ]
    for group in series["groupOrder"]:
        lines.extend([f"### {group}", ""])
        for item in (candidate for candidate in items if candidate["seriesPart"] == group):
            checked = "x" if item["status"] == "done" else " "
            official = item["personOrScope"]
            label = item["displayTitle"]
            bilingual = label if label == official else f"{label}（{official}）"
            if item.get("href"):
                action = f"[阅读页]({item['href']})"
            else:
                action = f"[官方资料]({item['sourceUrl']})"
            suffix = f" — {action}"
            if item.get("annotation"):
                suffix += f"；{item['annotation']}"
            lines.append(f"- [{checked}] {item['awardYear']} · {bilingual}{suffix}")
        lines.append("")
    lines.extend(
        [
            "## 来源登记",
            "",
            "| 来源 | 日期 | 用途 | 置信度 |",
            "|---|---:|---|---|",
            f"| [Nobel Prize API：prizes]({NOBEL_API_URL}) | {as_of} | 奖项年份、未颁奖年份、官方姓名与得主 ID | 高 |",
            f"| [Nobel Prize API：laureates]({NOBEL_LAUREATES_API_URL}) | {as_of} | 得主详情与官方资料页 | 高 |",
            f"| [Wikidata API]({WIKIDATA_API_URL}) | {as_of} | 简体中文显示名；缺失时回退官方英文名 | 中 |",
            "| `qrthoughts/**/*.md` | 当前检出 | 站内阅读笔记与候选匹配 | 高 |",
            "",
            "## 已知匹配边界",
            "",
            "- 福克纳的官方获奖年份是 1949；现有站内笔记标题写作 1994，故仅作候选链接，不改写原文。",
            "- 《切·米沃什诗选》可证明已有作品阅读，但原笔记未以诺奖系列命名，故作候选链接。",
            "- 其余 todo 只表示本站尚无对应公开阅读笔记。",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--hanyi-html", required=True, help="Downloaded official 1000-title HTML snapshot")
    parser.add_argument("--nobel-prizes-json", required=True, help="Downloaded Nobel prizes API JSON")
    parser.add_argument("--nobel-laureates-json", required=True, help="Downloaded Nobel laureates API JSON")
    parser.add_argument("--wikidata-labels-json", required=True, help="Downloaded Wikidata label map")
    parser.add_argument("--as-of", default=dt.date.today().isoformat(), help="Snapshot date (YYYY-MM-DD)")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    root = Path(args.root).resolve()
    data_path = root / "data" / "series-books.json"
    existing = load_json(data_path)
    preserved = [
        series
        for series in existing.get("series", [])
        if series.get("slug") not in {"hanyi-world-academic-classics", "nobel-literature"}
    ]
    notes = note_index(root)
    catalog = parse_hanyi_catalog(Path(args.hanyi_html))
    hanyi = hanyi_series(catalog, notes, args.as_of)
    nobel = nobel_series(
        load_json(Path(args.nobel_prizes_json)),
        load_json(Path(args.nobel_laureates_json)),
        load_json(Path(args.wikidata_labels_json)),
        notes,
        args.as_of,
    )
    payload = {"generatedAt": args.as_of, "series": preserved + [hanyi, nobel]}
    data_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    write_hanyi_markdown(root / "reading-lists" / "hanyi-world-academic-classics-unread.md", hanyi, args.as_of)
    write_nobel_markdown(root / "reading-lists" / "nobel-literature-reading-progress.md", nobel, args.as_of)
    print(
        "Generated reading series: "
        f"Hanyi {len(hanyi['items'])} ({hanyi['sourceSummary']['siteDoneWorks']} done), "
        f"Nobel {len(nobel['items'])} ({nobel['sourceSummary']['siteDoneLaureates']} done)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
