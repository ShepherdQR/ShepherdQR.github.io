#!/usr/bin/env python3
"""Regression checks for classification coverage, open extension and real notes."""
import copy
import unittest
from pathlib import Path

import build_knowledge_atlas as atlas
import generate_homepage_data

ROOT = Path(__file__).resolve().parents[1]


class KnowledgeAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.taxonomy = atlas.read(ROOT, 'knowledge-taxonomy.json')
        cls.standards = atlas.read(ROOT, 'knowledge-standards.json')
        cls.crosswalk = atlas.read(ROOT, 'knowledge-crosswalk.json')
        cls.assignments = atlas.read(ROOT, 'knowledge-assignments.json')
        cls.items = generate_homepage_data.collect_items(ROOT)
        cls.payload = atlas.build_payload(ROOT, cls.items)

    def test_exact_standard_inventories_are_independently_checked(self):
        self.assertEqual({k:len(v) for k,v in atlas.expected_codes().items()}, {'ford2015':42,'isced2013':80,'moe2022':184})
        broken = copy.deepcopy(self.standards)
        broken['sources'][0]['entries'].pop()
        broken['sources'][0]['count'] -= 1
        with self.assertRaisesRegex(ValueError, 'source inventory'):
            atlas.validate(self.taxonomy, broken, self.crosswalk, self.assignments)

    def test_unmapped_standard_and_unknown_targets_are_rejected(self):
        for mode in ('missing','unknown'):
            broken=copy.deepcopy(self.crosswalk)
            if mode=='missing':broken['mappings'].pop()
            else:broken['mappings'][0]['nodes']=['nonexistent']
            with self.assertRaises(ValueError):
                atlas.validate(self.taxonomy,self.standards,broken,self.assignments)

    def test_new_domain_can_be_added_without_reclassifying_old_knowledge(self):
        extended=copy.deepcopy(self.taxonomy)
        extended['domains'].append(dict(id='new-field',title='New field',family='formal',children=[dict(id='new-field.question',title='New question')],related=['math']))
        atlas.validate(extended,self.standards,self.crosswalk,self.assignments)

    def test_existing_branches_can_grow_more_levels(self):
        extended=copy.deepcopy(self.taxonomy)
        branch=extended['domains'][0]['children'][0]
        branch['children']=[dict(id=branch['id']+'.new-question',title='New question',children=[dict(id=branch['id']+'.new-question.detail',title='Further detail')])]
        atlas.validate(extended,self.standards,self.crosswalk,self.assignments)
        self.assertEqual(len(list(atlas.walk(branch))),3)

    def test_retired_ids_redirect_directly_to_live_nodes(self):
        extended=copy.deepcopy(self.taxonomy)
        extended['redirects']={'old-field':'systems'}
        atlas.validate(extended,self.standards,self.crosswalk,self.assignments)
        extended['redirects']['old-field']='missing'
        with self.assertRaisesRegex(ValueError,'redirect'):
            atlas.validate(extended,self.standards,self.crosswalk,self.assignments)

    def test_frontier_cannot_publish_a_dead_link(self):
        broken=copy.deepcopy(self.taxonomy)
        broken['frontiers'][0]['nodes']=['not-a-field']
        with self.assertRaisesRegex(ValueError,'frontier'):
            atlas.validate(broken,self.standards,self.crosswalk,self.assignments)

    def test_every_current_note_is_reachable_without_fabricated_items(self):
        expected={f"{i['type']}:{i['id']}" for i in self.items}
        self.assertEqual(set(self.payload['items']),expected)
        self.assertEqual(self.payload['unassigned'],[])
        reached=set().union(*(set(d['itemKeys']) for d in self.payload['domains']))
        self.assertEqual(reached,expected)
        for domain in self.payload['domains']:
            self.assertEqual(len(domain['itemKeys']),len(set(domain['itemKeys'])))

    def test_multi_subject_book_keeps_one_identity_and_correct_topics(self):
        book=self.payload['items']['Books:0151']
        self.assertEqual(book['canonicalHref'],'/books/0151/')
        self.assertIn('history.world',book['nodes'])
        self.assertIn('security.military',book['nodes'])
        # Medical reading must not inherit the historical Books -> Literature default.
        medical=self.payload['items']['Books:0156']
        self.assertIn('health.traditional',medical['nodes'])
        self.assertNotIn('literature',medical['nodes'])

    def test_no_javascript_fallback_links_every_actual_note(self):
        page=atlas.static_html(self.payload)
        for item in self.items:
            self.assertIn(f'href="{item["canonicalHref"]}"',page)
        for d in self.payload['domains']:
            for c in d['children']:
                self.assertIn(f'id="knowledge-{c["id"]}"',page)

    def test_provenance_is_not_inferred_from_a_topic(self):
        item=self.payload['items']['Thoughts:0018']
        self.assertEqual(item['origin'],'unspecified')
        self.assertEqual(item['evidence'],'unreviewed')


if __name__ == '__main__':
    unittest.main()
