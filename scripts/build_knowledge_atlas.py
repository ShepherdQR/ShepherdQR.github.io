#!/usr/bin/env python3
"""Build an open knowledge atlas from versioned taxonomy and editorial mappings.

Coverage means navigation coverage against the explicitly named inventories.
It never means all knowledge is known, validated, or present in this corpus.
"""
from __future__ import annotations

import copy
import html
import json
import re
from pathlib import Path

import article_pipeline

START = '<!-- KNOWLEDGE_ATLAS_STATIC_START -->'
END = '<!-- KNOWLEDGE_ATLAS_STATIC_END -->'


def expected_codes() -> dict[str, set[str]]:
    ford = {f'{i}.{n}' for i, count in enumerate([7, 11, 5, 5, 9, 5], 1) for n in range(1, count + 1)}
    isced = set()
    for prefix, digits in {
        '001':'1','002':'1','003':'1','011':'1234','021':'12345','022':'123','023':'12',
        '031':'1234','032':'12','041':'1234567','042':'1','051':'12','052':'12',
        '053':'123','054':'12','061':'123','071':'123456','072':'1234','073':'12',
        '081':'12','082':'1','083':'1','084':'1','091':'1234567','092':'123',
        '101':'12345','102':'12','103':'12','104':'1',
    }.items():
        isced.update(prefix + digit for digit in digits)
    moe = set()
    for category, count in enumerate([1, 2, 8, 3, 3, 3, 14, 39, 10, 12, 11, 5, 1, 7], 1):
        moe.update(f'{category:02d}{i:02d}' for i in range(1, count + 1))
    moe.difference_update({'0834', '1010'})
    moe.update('0151 0251 0252 0253 0254 0255 0256 0258 0351 0352 0353 0354 0355 0451 0452 0453 0454 0551 0552 0553 0651 0751 0851 0853 0854 0855 0856 0857 0858 0859 0860 0861 0862 0951 0952 0954 0955 1051 1052 1053 1054 1055 1056 1057 1058 1059 1152 1153 1154 1155 1156 1157 1251 1252 1253 1254 1255 1256 1257 1352 1353 1354 1355 1356 1357 1451 1452'.split())
    return {'ford2015': ford, 'isced2013': isced, 'moe2022': moe}


def read(root: Path, name: str) -> dict:
    return json.loads((root / 'data' / name).read_text(encoding='utf-8'))


def walk(node: dict):
    """Visit any depth without tying the data model to the current two levels."""
    yield node
    for child in node.get('children', []):
        yield from walk(child)


def validate(taxonomy: dict, standards: dict, crosswalk: dict, assignments: dict) -> None:
    nodes = {}
    families = {f['id'] for f in taxonomy['families']}
    domains = {d['id'] for d in taxonomy['domains']}
    for domain in taxonomy['domains']:
        if not re.fullmatch(r'[a-z][a-z0-9-]*', domain['id']):
            raise ValueError(f"Invalid root domain ID: {domain['id']}")
        if domain['family'] not in families or not domain['children']:
            raise ValueError(f"Invalid domain family/children: {domain['id']}")
        for node in walk(domain):
            ident = node['id']
            if ident in nodes or not re.fullmatch(r'[a-z][a-z0-9-]*(?:\.[a-z0-9-]+)*', ident):
                raise ValueError(f'Duplicate or invalid knowledge ID: {ident}')
            if node is not domain and not ident.startswith(domain['id'] + '.'):
                raise ValueError(f'Child outside its parent: {ident}')
            for child in node.get('children', []):
                if child['id'].rsplit('.', 1)[0] != ident:
                    raise ValueError(f'Child outside its immediate parent: {child["id"]}')
            nodes[ident] = node
        if not set(domain.get('related', [])).issubset(domains):
            raise ValueError(f"Unknown related domain: {domain['id']}")
    for old, new in taxonomy.get('redirects', {}).items():
        if old in nodes or new not in nodes:
            raise ValueError(f'Invalid retired knowledge ID redirect: {old} -> {new}')
    for frontier in taxonomy.get('frontiers', []):
        if not frontier.get('nodes') or not set(frontier['nodes']).issubset(nodes):
            raise ValueError(f"Invalid frontier links: {frontier.get('id')}")
    expected = expected_codes()
    if {s['id'] for s in standards['sources']} != set(expected):
        raise ValueError('Standard inventories do not match the declared baseline')
    inventory = set()
    for source in standards['sources']:
        codes = [e['code'] for e in source['entries']]
        if len(codes) != len(set(codes)) or set(codes) != expected[source['id']]:
            raise ValueError(f"Incomplete or duplicate source inventory: {source['id']}")
        if source['count'] != len(codes):
            raise ValueError(f"Incorrect source count: {source['id']}")
        inventory.update((source['id'], c) for c in codes)
    mapped = set()
    for mapping in crosswalk['mappings']:
        key = (mapping['standard'], mapping['code'])
        if key in mapped:
            raise ValueError(f'Duplicate standard mapping: {key}')
        mapped.add(key)
        if not mapping['nodes'] or not set(mapping['nodes']).issubset(nodes):
            raise ValueError(f'Unknown or missing mapping targets: {key}')
    if mapped != inventory:
        raise ValueError(f'Standard mapping coverage mismatch: missing={inventory-mapped}, extra={mapped-inventory}')
    for key, targets in assignments['items'].items():
        if not targets or not set(targets).issubset(nodes):
            raise ValueError(f'Invalid content assignment: {key}')


def build_payload(root: Path, items: list[dict]) -> dict:
    taxonomy = read(root, 'knowledge-taxonomy.json')
    standards = read(root, 'knowledge-standards.json')
    crosswalk = read(root, 'knowledge-crosswalk.json')
    assignments = read(root, 'knowledge-assignments.json')
    validate(taxonomy, standards, crosswalk, assignments)
    payload = copy.deepcopy(taxonomy)
    nodes = {n['id']: n for d in payload['domains'] for n in walk(d)}
    by_id = {}
    for node in nodes.values():
        node['itemKeys'] = []
    valid_origins = {'human', 'ai', 'collaborative', 'unspecified'}
    valid_evidence = {'unreviewed', 'conjecture', 'argument', 'formal-proof', 'empirical', 'contested', 'superseded'}
    unassigned = []
    for item in items:
        key = f"{item['type']}:{item['id']}"
        meta, _, _ = article_pipeline.read_markdown_document(root / item['sourcePath'])
        explicit = meta.get('knowledge_ids')
        targets = explicit if explicit else assignments['items'].get(key, [])
        if not isinstance(targets, list) or not set(targets).issubset(nodes):
            raise ValueError(f'Invalid knowledge_ids: {key}')
        origin = meta.get('contribution_origin', 'unspecified')
        evidence = meta.get('evidence_status', 'unreviewed')
        if origin not in valid_origins or evidence not in valid_evidence:
            raise ValueError(f'Invalid knowledge provenance: {key}')
        by_id[key] = {**{k: item[k] for k in ('type', 'id', 'title', 'summary', 'canonicalHref', 'published') if k in item},
                      'nodes': targets, 'mappingBasis': 'author-metadata' if explicit else 'editorial' if targets else 'unassigned',
                      'origin': origin, 'evidence': evidence}
        if not targets:
            unassigned.append(key)
        for ident in targets:
            parts = ident.split('.')
            for target in {'.'.join(parts[:i]) for i in range(1, len(parts)+1)}:
                if key not in nodes[target]['itemKeys']:
                    nodes[target]['itemKeys'].append(key)
    payload['items'] = by_id
    payload['unassigned'] = unassigned
    payload['coverage'] = []
    for source in standards['sources']:
        maps = {m['code']: m for m in crosswalk['mappings'] if m['standard'] == source['id']}
        payload['coverage'].append({k: source[k] for k in ('id', 'title', 'version', 'url', 'count', 'scope')})
        payload['coverage'][-1]['entries'] = [{**entry, 'nodes': maps[entry['code']]['nodes']} for entry in source['entries']]
    payload['counts'] = {'domains': len(payload['domains']), 'branches': len(nodes)-len(payload['domains']),
                         'articles': len(items), 'mappedArticles': len(items)-len(unassigned), 'standardEntries': sum(s['count'] for s in standards['sources'])}
    return payload


def static_html(payload: dict) -> str:
    esc = html.escape
    def branch_html(child: dict) -> str:
        chunks = [f'<details id="knowledge-{child["id"]}"><summary>{esc(child["title"])} · {len(child["itemKeys"])} 篇</summary>']
        for nested in child.get('children', []):
            chunks.append(branch_html(nested))
        if not child['itemKeys']:
            chunks.append('<p>这个分支尚无公开笔记。</p>')
        else:
            chunks.append('<ul>')
            for key in child['itemKeys']:
                item=payload['items'][key]
                chunks.append(f'<li><a href="{esc(item["canonicalHref"],quote=True)}">{esc(item["title"])}</a></li>')
            chunks.append('</ul>')
        chunks.append('</details>')
        return '\n'.join(chunks)
    lines = ['<div class="knowledge-static" id="knowledge-static">', '<p class="knowledge-static-intro">逐层打开领域，阅读其中的书籍与思考。</p>', '<div class="knowledge-static-grid">']
    for d in payload['domains']:
        lines.append(f'<a class="knowledge-static-tile" href="#knowledge-{d["id"]}"><span>{esc(d["title"])}</span><small>{len(d["itemKeys"])} 篇笔记</small></a>')
    lines.append('</div>')
    for d in payload['domains']:
        lines.extend([f'<details class="knowledge-static-domain" id="knowledge-{d["id"]}"><summary>{esc(d["title"])} · {len(d["itemKeys"])} 篇笔记</summary>',f'<p>{esc(d["description"])}</p>', '<div class="knowledge-static-branches">'])
        for child in d['children']:
            lines.append(branch_html(child))
        lines.append('</div><p>本领域全部笔记</p><ul>')
        for key in d['itemKeys']:
            item = payload['items'][key]
            lines.append(f'<li><a href="{esc(item["canonicalHref"],quote=True)}">{esc(item["title"])}</a></li>')
        if not d['itemKeys']:
            lines.append('<li>领域已建立，尚无公开笔记。</li>')
        lines.append('</ul></details>')
    if payload['unassigned']:
        lines.append('<details><summary>待归档的公开笔记</summary><ul>')
        for key in payload['unassigned']:
            item=payload['items'][key]
            lines.append(f'<li><a href="{esc(item["canonicalHref"],quote=True)}">{esc(item["title"])}</a></li>')
        lines.append('</ul></details>')
    lines.append('</div>')
    return '\n'.join(lines)


def build(root: Path, items: list[dict]) -> dict:
    payload = build_payload(root, items)
    (root/'knowledge-atlas-data.js').write_text('window.KNOWLEDGE_ATLAS = '+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8',newline='\n')
    index = root/'index.html'
    text=index.read_text(encoding='utf-8')
    if text.count(START)!=1 or text.count(END)!=1:
        raise ValueError('Homepage must have exactly one static knowledge atlas marker pair')
    prefix,rest=text.split(START)
    _,suffix=rest.split(END)
    index.write_text(prefix+START+'\n'+static_html(payload)+'\n'+END+suffix,encoding='utf-8',newline='\n')
    return payload['counts']
