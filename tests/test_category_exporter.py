"""Unit tests for InvenTree Category Exporter Plugin."""

import unittest
from unittest.mock import MagicMock, patch

try:
    from django.conf import settings
    if not settings.configured:
        settings.configure(USE_I18N=False)
except Exception:
    pass

try:
    from inventree_category_exporter.category_exporter import (
        CategoryExporterPlugin,
        build_category_tree,
    )
except ImportError:
    from category_exporter import (
        CategoryExporterPlugin,
        build_category_tree,
    )


class MockCategory:
    """Mock object simulating InvenTree PartCategory model."""

    def __init__(self, pk, name, parent_id=None, pathstring="", level=0, description=""):
        self.pk = pk
        self.id = pk
        self.name = name
        self.parent_id = parent_id
        self.pathstring = pathstring
        self.level = level
        self.description = description


class TestCategoryTreeBuilder(unittest.TestCase):
    """Tests for the tree text hierarchy builder."""

    def test_empty_categories(self):
        """Verify building tree from empty category list returns empty string."""
        self.assertEqual(build_category_tree([]), "")

    def test_single_root_category(self):
        """Verify single root category without children."""
        cats = [MockCategory(1, "Electronics")]
        self.assertEqual(build_category_tree(cats), "Electronics")

    def test_nested_tree_structure(self):
        """Verify multi-level hierarchy renders proper tree drawing characters."""
        cats = [
            MockCategory(1, "Electronics"),
            MockCategory(2, "Resistors", parent_id=1),
            MockCategory(3, "SMD", parent_id=2),
            MockCategory(4, "Through-Hole", parent_id=2),
            MockCategory(5, "Capacitors", parent_id=1),
            MockCategory(6, "Ceramic", parent_id=5),
        ]

        expected_lines = [
            "Electronics",
            "├── Resistors",
            "│   ├── SMD",
            "│   └── Through-Hole",
            "└── Capacitors",
            "    └── Ceramic",
        ]
        expected_tree = "\n".join(expected_lines)
        self.assertEqual(build_category_tree(cats), expected_tree)

    def test_multiple_roots(self):
        """Verify rendering multiple independent top-level categories."""
        cats = [
            MockCategory(1, "Mechanical"),
            MockCategory(2, "Screws", parent_id=1),
            MockCategory(3, "Electronic"),
            MockCategory(4, "Diodes", parent_id=3),
        ]

        expected_lines = [
            "Mechanical",
            "└── Screws",
            "Electronic",
            "└── Diodes",
        ]
        self.assertEqual(build_category_tree(cats), "\n".join(expected_lines))


class TestCategoryExporterPlugin(unittest.TestCase):
    """Tests for CategoryExporterPlugin views and datasets."""

    def setUp(self):
        self.plugin = CategoryExporterPlugin()
        self.sample_categories = [
            MockCategory(1, "Electronics", None, "Electronics", 0, "All electronics"),
            MockCategory(2, "Resistors", 1, "Electronics/Resistors", 1, None),
        ]

    def test_plugin_metadata(self):
        """Verify plugin metadata attributes."""
        self.assertEqual(self.plugin.NAME, "CategoryExporterPlugin")
        self.assertEqual(self.plugin.SLUG, "category_exporter")
        self.assertEqual(self.plugin.TITLE, "Category Exporter")
        self.assertEqual(self.plugin.VERSION, "1.0.0")
        self.assertTrue(bool(self.plugin.DESCRIPTION))

    def test_setup_urls(self):
        """Verify setup_urls defines expected endpoints."""
        urls = self.plugin.setup_urls()
        self.assertIsNotNone(urls)
        self.assertEqual(len(urls), 4)

    def test_generate_dataset(self):
        """Verify tablib dataset generation."""
        dataset = self.plugin._generate_dataset(self.sample_categories)
        self.assertEqual(dataset.headers, ['ID', 'Name', 'Path', 'Level', 'Description'])
        self.assertEqual(len(dataset), 2)

        # First row
        row0 = dataset[0]
        self.assertEqual(row0[0], 1)
        self.assertEqual(row0[1], "Electronics")
        self.assertEqual(row0[2], "Electronics")
        self.assertEqual(row0[3], 0)
        self.assertEqual(row0[4], "All electronics")

        # Second row (None description converted to empty string)
        row1 = dataset[1]
        self.assertEqual(row1[0], 2)
        self.assertEqual(row1[1], "Resistors")
        self.assertEqual(row1[4], "")

    def test_export_csv(self):
        """Verify CSV export endpoint response."""
        response = self.plugin.export_csv(request=None, categories=self.sample_categories)
        content_type = response.headers.get("Content-Type") if hasattr(response, "headers") else response.get("Content-Type", "")
        self.assertIn("text/csv", content_type)
        disposition = response.headers.get("Content-Disposition") if hasattr(response, "headers") else response.get("Content-Disposition", "")
        self.assertIn('attachment; filename="categories_', disposition)
        self.assertTrue(disposition.endswith('.csv"'))

    def test_export_xlsx(self):
        """Verify XLSX export endpoint response."""
        response = self.plugin.export_xlsx(request=None, categories=self.sample_categories)
        content_type = response.headers.get("Content-Type") if hasattr(response, "headers") else response.get("Content-Type", "")
        self.assertIn("spreadsheetml.sheet", content_type)
        disposition = response.headers.get("Content-Disposition") if hasattr(response, "headers") else response.get("Content-Disposition", "")
        self.assertIn('attachment; filename="categories_', disposition)
        self.assertTrue(disposition.endswith('.xlsx"'))

    def test_export_tree(self):
        """Verify text tree export endpoint response."""
        response = self.plugin.export_tree(request=None, categories=self.sample_categories)
        content_type = response.headers.get("Content-Type") if hasattr(response, "headers") else response.get("Content-Type", "")
        self.assertIn("text/plain", content_type)
        disposition = response.headers.get("Content-Disposition") if hasattr(response, "headers") else response.get("Content-Disposition", "")
        self.assertIn('attachment; filename="categories_tree_', disposition)
        self.assertTrue(disposition.endswith('.txt"'))

        content = response.content.decode("utf-8") if isinstance(response.content, bytes) else response.content
        self.assertIn("Electronics", content)
        self.assertIn("└── Resistors", content)

    def test_index_view(self):
        """Verify index HTML view."""
        response = self.plugin.index_view(request=None)
        content_type = response.headers.get("Content-Type") if hasattr(response, "headers") else response.get("Content-Type", "")
        self.assertIn("text/html", content_type)
        content = response.content.decode("utf-8") if isinstance(response.content, bytes) else response.content
        self.assertIn("InvenTree Category Exporter", content)
        self.assertIn("export/csv/", content)
        self.assertIn("export/xlsx/", content)
        self.assertIn("export/tree/", content)


if __name__ == "__main__":
    unittest.main()
