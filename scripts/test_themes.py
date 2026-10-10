"""Theme package boundaries and deterministic output; runtime checks live in test_theme_browser.cjs."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import build_themes

ROOT = Path(__file__).resolve().parents[1]


class ThemeContractTests(unittest.TestCase):
    def fixture(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        shutil.copytree(ROOT / "themes", root / "themes")
        (root / "includes/js").mkdir(parents=True)
        return root

    def change(self, root, path, **values):
        file = root / path
        data = json.loads(file.read_text(encoding="utf-8"))
        data.update(values)
        file.write_text(json.dumps(data), encoding="utf-8")

    def test_all_published_packages_use_the_same_content_contract(self):
        registry = build_themes.load_registry(ROOT)
        self.assertEqual(registry["default"], "weave")
        self.assertEqual({t["id"] for t in registry["themes"]}, {"weave", "twilight", "tomography"})
        self.assertTrue(all("article" in t["surfaces"] for t in registry["themes"]))

    def test_outside_theme_assets_are_rejected(self):
        root = self.fixture()
        (root / "private.js").write_text("private", encoding="utf-8")
        self.change(root, "themes/weave/theme.json", scene="themes/../private.js")
        with self.assertRaises(ValueError):
            build_themes.load_registry(root)

    def test_unknown_default_is_rejected(self):
        root = self.fixture()
        self.change(root, "themes/registry.json", default="missing")
        with self.assertRaises(ValueError):
            build_themes.load_registry(root)

    def test_incompatible_package_is_rejected(self):
        root = self.fixture()
        self.change(root, "themes/twilight/theme.json", contractVersion=999)
        with self.assertRaises(ValueError):
            build_themes.load_registry(root)

    def test_unknown_fallback_is_rejected(self):
        root = self.fixture()
        self.change(root, "themes/tomography/theme.json", fallbackTheme="missing")
        with self.assertRaises(ValueError):
            build_themes.load_registry(root)

    def test_build_is_deterministic_and_does_not_change_source(self):
        root = self.fixture()
        source = (root / "themes/registry.json").read_bytes()
        build_themes.build(root)
        first = (root / "themes/registry.js").read_bytes()
        build_themes.build(root)
        self.assertEqual(first, (root / "themes/registry.js").read_bytes())
        self.assertEqual(source, (root / "themes/registry.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
