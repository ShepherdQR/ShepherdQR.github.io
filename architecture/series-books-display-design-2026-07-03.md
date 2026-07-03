# Series Books Display Design

Date: 2026-07-03
Status: Design proposal
Scope: Plan a reusable display form for `丛书 / 系列书`, with `[20世纪世界诗歌译丛]` as the first pilot series.

## Executive Summary

Use a three-level navigation model:

1. Home page adds a `丛书 / 系列书` collection tile.
2. The tile opens a series index page, `series.html`, where each block is one clickable series.
3. Clicking `[20世纪世界诗歌译丛]` opens a series detail page, for example `series/20th-century-world-poetry/`, with `Done` and `Todo` sections and one stable clickable block per concrete work.

This is better than putting the whole series directly on the homepage. The homepage remains a navigation surface, the series index becomes reusable for future collections, and each series detail page can carry enough structure for volumes, people, anthologies, progress, and reading-note links.

For `[20世纪世界诗歌译丛]`, the first data pass should treat `上 / 下`, `上 / 中 / 下`, `001 / 002 / 003`, and similar suffixes as one work item. Individual poet books are grouped by person; anthology books are grouped by their scope, such as `二十世纪冰岛诗选` or `美洲译诗文选`.

## Source Register

| Source | Date/version | Used for | Confidence |
|---|---:|---|---|
| `README.md` | Current checkout | Confirms Markdown-first workflow, generated clean URLs, and build/validation expectations. | High |
| `scripts/generate_homepage_data.py` | Current checkout | Confirms generated data fields currently include note metadata and clean links, but not rich series metadata. | High |
| `scripts/build_site.py` | Current checkout | Confirms static alias pages and site indexes are generated from Markdown-backed items. | High |
| `index.html` + `includes/css/homepage.css` | Current checkout | Confirms the homepage already has a `Collections` tile pattern suitable for `丛书 / 系列书`. | High |
| `books.html` + `includes/js/archive-page.js` | Current checkout | Confirms current Books view is a flat type-filtered archive. | High |
| `qrthoughts/**/*.md` filename scan | 2026-07-03 | Identifies existing site Markdown names for `[20世纪世界诗歌译丛]`. | High for filenames |
| `C:\MyPower\BooksDone\Literature\Poem\[20世纪世界诗歌译丛]` filename scan | 2026-07-03 | Identifies local completed series book names only; file contents were not read. | High for filenames |
| `C:\MyPower\BooksGoingOn\诗歌` filename scan | 2026-07-03 | Identifies local ongoing/todo poetry book names only; file contents were not read. | Medium, because the folder also contains non-series and duplicate-staging items |

## Current Site Constraints

The site is already Markdown-first:

- Source notes live under `qrthoughts/yearYYYY/monthM/`.
- `scripts/build_site.py` regenerates `homepage-data.js`, clean article pages such as `/books/0089/`, `sitemap.xml`, and `includes/atom.xml`.
- `homepage-data.js` is currently flat note data: `type`, `id`, `title`, dates, `href`, `canonicalHref`, `legacyHref`, and `sourcePath`.
- `books.html` is a generated archive view filtered to `type === "Books"`, grouped by year.
- The homepage already has a `Collections` area with clickable blocks for `Thoughts`, `Books`, `Study`, and `Videos`.

The missing layer is not another archive filter. A series is a cross-note reading object: it needs progress, ordering by series volume, volume merging, and links from a work item to one or more notes.

## Recommended Information Architecture

### Level 1: Home Entry

Add one collection tile in the existing `Collections` grid:

- Label: `Series`
- Chinese display name if desired: `丛书 / 系列书`
- Subtext: `按套书追踪阅读进度`
- Link: `./series.html`

This should be a normal collection tile, not a special oversized button. It will feel consistent with the current homepage and will keep the first viewport calm.

### Level 2: Series Index

Create `series.html` as the reusable index page.

Each series block should be clickable and should show:

- Series title, for example `[20世纪世界诗歌译丛]`
- Short description
- Progress summary, for example `21 site notes / 23 local done works / 26 todo works`
- Coverage tags, for example `Poetry`, `Translation`, `20th century`
- Last updated date

The page should start with a compact heading and then a grid/list of series blocks. It should not become a landing page; it is a working catalog.

### Level 3: Series Detail Page

Create one page per series:

```text
series/20th-century-world-poetry/index.html
```

The detail page should contain:

- Header: title, short description, progress numbers, last data refresh date.
- Status controls: `All`, `Done`, `Todo`.
- Series-part controls: `第一辑`, `第二辑`, `第三辑`, `第四辑`, `第五辑`.
- Sort controls: `按辑`, `按作者/对象`, `按阅读日期`.
- Main list: one block per normalized work item.

Use URL fragments or query parameters for shareable states:

```text
/series/20th-century-world-poetry/#done
/series/20th-century-world-poetry/#todo
/series/20th-century-world-poetry/?part=第三辑&status=todo
```

## Work Item Card

Each book/work block should be stable, compact, and clickable.

Fields:

- Display title: `耶胡达·阿米亥诗`
- Person or scope: `耶胡达·阿米亥`; for anthologies, use `美洲现代诗歌 / 选本`
- Series part: `第一辑`
- Status: `Done`, `Todo`, or `Candidate match`
- Volumes: `上册 + 下册`, `上中下`, or empty
- Public link:
  - If a reading note exists, link to `/books/NNNN/`.
  - If no reading note exists, link to the stable item anchor on the series detail page, such as `#book-gregory-corso`, and show `待写阅读页`.
- Source label: `site-md`, `local-done`, `local-going-on`, or `manual-alias`.

Card behavior:

- The whole block is clickable.
- A visible secondary link can say `阅读页` only when a public note exists.
- Todo items should not link to private local file paths on the public site.
- When a Todo item later gets a Books note, only the data entry changes; the visual block stays in place.

## Data Model

Use a small committed data file, then render static pages from it.

Recommended file:

```text
data/series-books.json
```

Example:

```json
{
  "series": [
    {
      "slug": "20th-century-world-poetry",
      "title": "[20世纪世界诗歌译丛]",
      "description": "河北教育出版社二十世纪世界诗歌译丛阅读进度。",
      "tags": ["Poetry", "Translation", "20th century"],
      "items": [
        {
          "workId": "yehuda-amichai-poems",
          "displayTitle": "耶胡达·阿米亥诗",
          "personOrScope": "耶胡达·阿米亥",
          "seriesPart": "第一辑",
          "status": "done",
          "volumes": ["上册", "下册"],
          "href": "/books/0015/",
          "noteId": "0015",
          "sourceNames": [
            "[20世纪世界诗歌译丛](第一辑)耶胡达·阿米亥诗_上册.pdf",
            "[20世纪世界诗歌译丛](第一辑)耶胡达·阿米亥诗_下册.pdf"
          ]
        }
      ]
    }
  ]
}
```

Why JSON instead of deriving everything from `homepage-data.js`:

- Existing Markdown metadata does not yet encode series part, volume grouping, person/scope, or todo works.
- Todo works may not have public Markdown notes yet.
- Local file paths should not be exposed on the public site.
- A JSON layer allows manual correction for punctuation variants such as `阿蒂拉·尤若夫` vs `阿蒂拉-尤若夫`.

Later, the Books Markdown front matter can grow optional fields:

```yaml
series: "[20世纪世界诗歌译丛]"
series_slug: "20th-century-world-poetry"
series_part: "第二辑"
work_id: "w-b-yeats-poems"
work_title: "叶芝诗集"
volume_group: "上中下"
```

The long-term direction can be: Markdown front matter is authoritative for published reading notes; `data/series-books.json` remains authoritative for todo, local inventory, and manual matching.

## Normalization Rules

The first collector should only read filenames, not book contents.

Normalize in this order:

1. Remove file extension.
2. Remove the series prefix: `[20世纪世界诗歌译丛](第N辑)`.
3. Remove obvious publisher/translator suffixes when they are metadata, while preserving meaningful title text. Keep original filenames in `sourceNames`.
4. Convert punctuation variants for matching only:
   - `·`, `-`, `_`, and missing separators should not prevent a match.
   - Full-width and half-width parentheses should be normalized for matching.
5. Merge volume suffixes:
   - `上`, `中`, `下`
   - `上册`, `中册`, `下册`
   - `-上`, `-下`
   - `_上册`, `_下册`
   - `001`, `002`, `003`
6. Mark folders named like `重复-不处理的` as excluded unless manually overridden.
7. If the same normalized work appears in Done and Todo, Done wins.

Manual alias examples needed for this pilot:

| Local/source variant | Site/normalized variant |
|---|---|
| `约翰·阿什贝利诗-上/下` | `约翰阿什贝利诗选上下册` |
| `阿蒂拉·尤若夫诗选` | `阿蒂拉-尤若夫诗选` |
| `默温诗选001/002/003` | `默温诗选上中下册` |
| `叶芝诗集 上/中/下` | candidate site note: `叶芝` |
| `博尔赫斯诗选` | candidate site note: `博尔赫斯` |

## Pilot Inventory: `[20世纪世界诗歌译丛]`

This inventory is filename-only. It is meant to seed the series data file and validation logic.

Summary:

- Local Done source: 30 files, normalized to 23 work items.
- Local GoingOn source: 35 series-prefixed files plus one non-series poetry ePub, normalized to 26 todo work items after excluding the explicit duplicate-staging folder.
- Site Markdown source: 21 `[20世纪世界诗歌译丛]`-named Books Markdown files.
- Two local Done works appear to have possible site notes without the series name in the Markdown filename: `博尔赫斯诗选` and `叶芝诗集`.

### Done Works

| Series part | Work item | Site note |
|---|---|---|
| 第一辑 | 安东尼奥·马查多诗选 | `/books/0012/` |
| 第一辑 | 保罗·策兰诗文选 | `/books/0013/` |
| 第一辑 | 里尔克诗选 | `/books/0014/` |
| 第一辑 | 耶胡达·阿米亥诗 | `/books/0015/` |
| 第一辑 | 伊丽莎白·毕肖普诗选 | `/books/0017/` |
| 第一辑 | 伊凡·哥尔诗选 | `/books/0019/` |
| 第一辑 | 狄兰·托马斯诗选 | `/books/0020/` |
| 第一辑 | 卡瓦菲斯诗集 | `/books/0022/` |
| 第一辑 | 切·米沃什诗选 | `/books/0023/` |
| 第二辑 | 吉皮乌斯诗选 | `/books/0040/` |
| 第二辑 | 非洲现代诗选 | `/books/0045/` |
| 第二辑 | 美洲译诗文选 | `/books/0063/` |
| 第二辑 | 曼德尔施塔姆诗选 | `/books/0074/` |
| 第二辑 | 默温诗选 | `/books/0080/` |
| 第二辑 | 聂鲁达诗选 | `/books/0081/` |
| 第二辑 | 索德格朗诗全集 | `/books/0086/` |
| 第二辑 | 约翰·阿什贝利诗 | `/books/0089/` |
| 第二辑 | 博尔赫斯诗选 | candidate: `/books/0072/` |
| 第二辑 | 叶芝诗集 | candidate: `/books/0057/` |
| 第三辑 | 阿蒂拉·尤若夫诗选 | `/books/0090/` |
| 第三辑 | 波普拉夫斯基诗选 | `/books/0097/` |
| 第三辑 | 二十世纪冰岛诗选 | `/books/0101/` |
| 第三辑 | 勃洛克抒情诗选 | `/books/0113/` |

### Todo Works

| Series part | Work item | Note |
|---|---|---|
| 第三辑 | 菲利普·拉金诗选 | todo |
| 第三辑 | 伽姆扎托夫爱情诗选 | todo |
| 第三辑 | 格雷戈里·柯索诗 | merge 上/下 |
| 第三辑 | 特兰斯特罗默诗选 | todo |
| 第三辑 | 沃伦诗选 | todo |
| 第三辑 | 英国当代诗选 | anthology |
| 第四辑 | 奥克塔维奥·帕斯诗选 | todo |
| 第四辑 | 保尔·艾吕雅诗选 | todo |
| 第四辑 | 二十世纪英语诗选 | merge 上/中/下 |
| 第四辑 | 古米廖夫诗选 | todo |
| 第四辑 | 鲁文·达里奥诗选 | todo |
| 第四辑 | 梅利尔诗选 | todo |
| 第四辑 | 欧美现代诗歌流派 | merge 上/中/下 |
| 第四辑 | 英美十人诗选 | anthology |
| 第四辑 | 1950年后的美国诗歌：革新者和局外人 | merge 上/下 from `ok-待整理` |
| 第四辑 | 彼得·霍恩诗选 | from `ok-待整理` |
| 第五辑 | R.S.托马斯自选诗集：1946-1968 | todo |
| 第五辑 | 安娜·布兰迪亚娜诗选 | todo |
| 第五辑 | 北欧现代诗选 | anthology |
| 第五辑 | 德瑞克·沃尔科特诗选 | todo |
| 第五辑 | 二十世纪俄罗斯流亡诗选 | merge 上/下 |
| 第五辑 | 费尔南多·佩索阿诗选 | todo |
| 第五辑 | 谷川俊太郎诗选 | todo |
| 第五辑 | 卡夫列拉·米斯特 | todo |
| 第五辑 | 马里奥·贝内德蒂 | todo |
| 第五辑 | 雅姆抒情诗选 | todo |

Excluded from this pilot:

- `C:\MyPower\BooksGoingOn\诗歌\狄兰·托马斯诗选(英汉对照)狄兰-托马斯-海岸译.epub`: poetry book, but not a `[20世纪世界诗歌译丛]` filename.
- `第四辑\ok-待整理\重复-不处理的\1950年后的美国诗-上/下`: explicit duplicate-staging folder.

## Existing Site Markdown Name Analysis

The existing site has 21 Markdown filenames that explicitly contain `[20世纪世界诗歌译丛]`:

| ID | Series part | Filename title pattern | Normalized work |
|---|---|---|---|
| 0012 | 第一辑 | `安东尼奥·马查多诗选` | 安东尼奥·马查多诗选 |
| 0013 | 第一辑 | `保罗·策兰诗文选` | 保罗·策兰诗文选 |
| 0014 | 第一辑 | `里尔克诗选` | 里尔克诗选 |
| 0015 | 第一辑 | `耶胡达·阿米亥诗选` | 耶胡达·阿米亥诗 |
| 0017 | 第一辑 | `伊丽莎白·毕肖普诗选` | 伊丽莎白·毕肖普诗选 |
| 0019 | 第一辑 | `伊凡·哥尔诗选` | 伊凡·哥尔诗选 |
| 0020 | 第一辑 | `狄兰·托马斯诗选` | 狄兰·托马斯诗选 |
| 0022 | 第一辑 | `卡瓦菲斯诗集` | 卡瓦菲斯诗集 |
| 0023 | 第一辑 | `切·米沃什诗选` | 切·米沃什诗选 |
| 0040 | 第二辑 | `吉皮乌斯诗选` | 吉皮乌斯诗选 |
| 0045 | 第二辑 | `非洲现代诗选上下册` | 非洲现代诗选 |
| 0063 | 第二辑 | `美洲译诗文选` | 美洲译诗文选 |
| 0074 | 第二辑 | `曼德尔施塔姆诗选` | 曼德尔施塔姆诗选 |
| 0080 | 第二辑 | `默温诗选上中下册` | 默温诗选 |
| 0081 | 第二辑 | `聂鲁达诗选` | 聂鲁达诗选 |
| 0086 | 第二辑 | `索德格朗诗全集` | 索德格朗诗全集 |
| 0089 | 第二辑 | `约翰阿什贝利诗选上下册` | 约翰·阿什贝利诗 |
| 0090 | 第三辑 | `阿蒂拉-尤若夫诗选` | 阿蒂拉·尤若夫诗选 |
| 0097 | 第三辑 | `波普拉夫斯基诗选` | 波普拉夫斯基诗选 |
| 0101 | 第三辑 | `二十世纪冰岛诗选` | 二十世纪冰岛诗选 |
| 0113 | 第三辑 | `勃洛克抒情诗选` | 勃洛克抒情诗选 |

Naming issues the design must handle:

- Some multi-volume books already appear as one Markdown note with `上下册` or `上中下册`.
- Some local filenames use `·`, while site filenames may omit it or use `-`.
- Site filenames and local filenames do not always preserve the same display title, so matching should use explicit `workId` plus alias rules.
- `博尔赫斯` and `叶芝` have possible Books notes, but the filenames do not explicitly mark them as `[20世纪世界诗歌译丛]`; they should be manually confirmed before linking.

## Page Design Details

### Visual Form

Use the existing quiet reading-site style:

- Same serif-first page typography as the homepage.
- Same paper background and restrained borders.
- Cards no larger than necessary; keep series/work cards at `border-radius: 8px` or less.
- Avoid a marketing-style hero. The first screen should already show catalog controls and the first series/work entries.

### Series Index Card

Example content:

```text
[20世纪世界诗歌译丛]
20th-century translated poetry reading map
21 site notes · 23 done works · 26 todo works
第一辑 - 第五辑
```

Click target:

```text
./series/20th-century-world-poetry/
```

### Series Detail Work Card

Example Done card:

```text
Done · 第一辑 · 上/下
耶胡达·阿米亥诗
耶胡达·阿米亥
阅读页 /books/0015/
```

Example Todo card:

```text
Todo · 第三辑 · 上/下
格雷戈里·柯索诗
格雷戈里·柯索
待写阅读页
```

Todo card click target:

```text
#book-gregory-corso-poems
```

When the reading note is later created, this changes to `/books/NNNN/`.

## Build Plan

### Phase 1: Data and Validation

Add:

- `data/series-books.json`
- `scripts/collect_series_books.py` or a similar local-only helper for filename collection
- `scripts/validate_series_books.py`

Validation should check:

- Unique `series.slug`
- Unique `workId` within each series
- Valid status values
- Existing `href` targets for Done items
- No local absolute file paths in public JSON
- Multi-volume groups are represented by one item

### Phase 2: Static Pages

Add:

- `series.html`
- `series/20th-century-world-poetry/index.html`
- `includes/css/series.css`
- `includes/js/series-page.js`

Update:

- `index.html`: add the `Series` collection tile.
- `scripts/build_site.py`: include static series paths in `sitemap.xml` if they are generated.
- `scripts/validate_site.py`: validate series page links.

### Phase 3: Metadata Integration

Add optional series metadata to existing Books Markdown files. Do this gradually, starting with the 21 explicit `[20世纪世界诗歌译丛]` notes.

The page should work before every old note has perfect metadata, because `data/series-books.json` can bridge the old filenames.

### Phase 4: Future Series

Once this pilot works, the same structure can support:

- Nobel literature books
- Computer science series
- Philosophy series
- Any future author/project reading sequence

## Acceptance Criteria

The pilot is complete when:

- The homepage has one clear `丛书 / 系列书` entry.
- `series.html` lists `[20世纪世界诗歌译丛]` as a clickable series block.
- The detail page shows Done and Todo sections without mixing private local paths into public HTML/JS.
- Multi-volume works are unified as one block.
- Done items link to public `/books/NNNN/` pages when a note exists.
- Todo items have stable anchors and do not create dead external links.
- Validation catches missing public links, duplicate work IDs, and accidental local path leakage.

## Open Questions

- Should `博尔赫斯` and `叶芝` be linked as `[20世纪世界诗歌译丛]` entries even though their existing Markdown filenames do not include the series name?
- Should each Todo item get a generated placeholder page, or is a stable detail-page anchor enough until the reading note exists?
- Should the visible label be `Series`, `Collections`, `丛书`, or `丛书 / 系列书`? The data model can use `Series`; the UI can use Chinese.
- Should anthology entries be visually separated from person/poet entries, or only tagged with `anthology`?

## Recommended First Implementation Slice

Implement the smallest useful version:

1. Create `data/series-books.json` with the inventory above.
2. Create `series.html` and one detail page for `[20世纪世界诗歌译丛]`.
3. Add the homepage collection tile.
4. Validate that all existing `/books/NNNN/` links resolve.

Do not edit every historical Books note in the first slice. The design should prove the public navigation and the data contract first, then backfill front matter metadata safely.
