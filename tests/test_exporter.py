"""Unit tests for the export logic (no InvenTree / database needed).

Run with:  python -m unittest discover -s tests -v
"""

import unittest
from types import SimpleNamespace

from inventree_category_exporter.exporter import (
    HEADERS,
    build_category_tree,
    category_rows,
    sanitize_cell,
)


def cat(pk, name, parent_id=None, pathstring='', level=0, description='', **extra):
    """Object with the (annotated) PartCategory attributes used by the exporter."""
    values = {
        'default_location_id': None,
        'parent_default_location': None,
        'default_keywords': None,
        'part_count': 0,
        'subcategories': 0,
        'structural': False,
        'icon': '',
    }
    values.update(extra)
    return SimpleNamespace(
        pk=pk, name=name, parent_id=parent_id, pathstring=pathstring or name, level=level, description=description,
        **values,
    )


class TreeTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(build_category_tree([]), '')

    def test_single_root(self):
        self.assertEqual(build_category_tree([cat(1, 'Electronics')]), 'Electronics')

    def test_nested(self):
        cats = [
            cat(1, 'Electronics'),
            cat(2, 'Resistors', 1),
            cat(3, 'SMD', 2),
            cat(4, 'Through-Hole', 2),
            cat(5, 'Capacitors', 1),
            cat(6, 'Ceramic', 5),
        ]
        expected = [
            'Electronics',
            '├── Resistors',
            '│   ├── SMD',
            '│   └── Through-Hole',
            '└── Capacitors',
            '    └── Ceramic',
        ]
        self.assertEqual(build_category_tree(cats), '\n'.join(expected))

    def test_multiple_roots(self):
        cats = [cat(1, 'Mechanical'), cat(2, 'Screws', 1), cat(3, 'Electronic'), cat(4, 'Diodes', 3)]
        expected = ['Mechanical', '└── Screws', 'Electronic', '└── Diodes']
        self.assertEqual(build_category_tree(cats), '\n'.join(expected))

    def test_subtree_starts_at_selected_category(self):
        """A category whose parent is not exported is a root."""
        cats = [cat(2, 'Resistors', 1), cat(3, 'SMD', 2), cat(4, 'THT', 2)]
        self.assertEqual(build_category_tree(cats), 'Resistors\n├── SMD\n└── THT')

    def test_deep_tree_no_recursion_limit(self):
        cats = [cat(1, 'c1')] + [cat(i, f'c{i}', i - 1) for i in range(2, 3000)]
        lines = build_category_tree(cats).split('\n')
        self.assertEqual(len(lines), 2999)
        self.assertTrue(lines[-1].endswith('└── c2999'))


class RowTests(unittest.TestCase):
    def test_rows(self):
        rows = category_rows([
            cat(1, 'Electronics', None, 'Electronics', 0, 'All electronics', default_location_id=10,
                default_keywords='elec', part_count=7, subcategories=1, structural=True, icon='ti:cpu:outline'),
            cat(2, 'Resistors', 1, 'Electronics/Resistors', 1, None, parent_default_location=10, part_count=5),
        ], locations={10: 'Warehouse/Shelf A'}, starred={2})
        self.assertEqual(len(HEADERS), 15)
        self.assertTrue(all(len(row) == len(HEADERS) for row in rows))
        self.assertEqual(rows[0], [
            1, 'Electronics', 'Electronics', 0, 'All electronics', '', '', 'Warehouse/Shelf A', '', 'elec',
            7, 1, True, False, 'ti:cpu:outline',
        ])
        self.assertEqual(rows[1], [
            2, 'Resistors', 'Electronics/Resistors', 1, '', 1, 'Electronics', '', 'Warehouse/Shelf A', '',
            5, 0, False, True, '',
        ])

    def test_parent_name_outside_export(self):
        """Sub-tree export: the parent of the selected category comes from parent_names."""
        rows = category_rows([cat(2, 'Resistors', 1), cat(3, 'SMD', 2)], parent_names={1: 'Electronics'})
        column = HEADERS.index('Parent Name')
        self.assertEqual([row[column] for row in rows], ['Electronics', 'Resistors'])

    def test_unknown_location_is_empty(self):
        row = category_rows([cat(1, 'A', default_location_id=99)])[0]
        self.assertEqual(row[HEADERS.index('Default Location')], '')

    def test_formula_injection_is_neutralised(self):
        self.assertEqual(sanitize_cell('=HYPERLINK("x")'), '\'=HYPERLINK("x")')
        self.assertEqual(sanitize_cell('@SUM(A1)'), "'@SUM(A1)")
        self.assertEqual(sanitize_cell('Resistors'), 'Resistors')
        self.assertEqual(sanitize_cell(5), 5)


class DatasetTests(unittest.TestCase):
    def setUp(self):
        try:
            import tablib  # noqa: F401
        except ImportError:
            self.skipTest('tablib not installed')

    def test_csv_and_xlsx(self):
        from inventree_category_exporter.exporter import build_dataset

        dataset = build_dataset([cat(1, 'Electronics', description='All')])
        self.assertEqual(dataset.headers, HEADERS)
        self.assertTrue(dataset.export('csv').startswith(','.join(HEADERS)))
        self.assertTrue(dataset.export('xlsx').startswith(b'PK'))


if __name__ == '__main__':
    unittest.main()
