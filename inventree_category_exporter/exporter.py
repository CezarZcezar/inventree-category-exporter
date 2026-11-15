"""Export logic for part categories.

This module has no Django / InvenTree imports, so it can be unit tested on its own.
A "category" is any object with the ``part.models.PartCategory`` attributes used
below, annotated like ``part.serializers.CategorySerializer.annotate_queryset``
(``part_count``, ``subcategories``, ``parent_default_location``).
"""

from __future__ import annotations

from collections.abc import Iterable

HEADERS = [
    'ID',
    'Name',
    'Path',
    'Level',
    'Description',
    'Parent Category',
    'Default Location',
    'Parent Default Location',
    'Default Keywords',
    'Parts',
    'Subcategories',
    'Structural',
    'Starred',
    'Icon',
]

# Leading characters which spreadsheet applications interpret as a formula
# (OWASP "CSV injection"). Values starting with them are prefixed with a quote.
FORMULA_PREFIXES = ('=', '+', '-', '@', '\t', '\r')


def sanitize_cell(value):
    """Neutralise text values which a spreadsheet would evaluate as a formula."""
    if isinstance(value, str) and value.startswith(FORMULA_PREFIXES):
        return "'" + value
    return value


def category_rows(categories: Iterable, locations: dict | None = None, starred: set | None = None) -> list[list]:
    """Return one row per category, matching HEADERS.

    Arguments:
        categories: Annotated categories
        locations: Map of stock location pk -> location path (for the location columns)
        starred: Set of category pks starred by the current user
    """
    locations = locations or {}
    starred = starred or set()

    def location(pk):
        return sanitize_cell(locations.get(pk, '')) if pk else ''

    return [
        [
            category.pk,
            sanitize_cell(category.name),
            sanitize_cell(category.pathstring or ''),
            category.level,
            sanitize_cell(category.description or ''),
            category.parent_id or '',
            location(category.default_location_id),
            location(category.parent_default_location),
            sanitize_cell(category.default_keywords or ''),
            category.part_count or 0,
            category.subcategories or 0,
            bool(category.structural),
            category.pk in starred,
            sanitize_cell(category.icon or ''),
        ]
        for category in categories
    ]


def build_dataset(categories: Iterable, locations: dict | None = None, starred: set | None = None):
    """Return a tablib Dataset with the category rows."""
    import tablib

    dataset = tablib.Dataset(headers=HEADERS, title='Categories')

    for row in category_rows(categories, locations, starred):
        dataset.append(row)

    return dataset


def build_category_tree(categories: Iterable) -> str:
    """Return a text tree (like the Linux ``tree`` command) of the categories.

    Categories whose parent is not part of the given list are treated as roots,
    so a sub-tree export starts at the selected category.
    The input order is kept for siblings (use MPTT order: ``tree_id``, ``lft``).
    """
    categories = list(categories)
    known = {category.pk for category in categories}

    children: dict = {}
    roots = []

    for category in categories:
        if category.parent_id in known:
            children.setdefault(category.parent_id, []).append(category)
        else:
            roots.append(category)

    lines = []

    # Iterative depth-first walk (no recursion limit for very deep trees)
    for root in roots:
        lines.append(root.name)
        # Stack of [siblings, index of the next sibling, line prefix]
        stack = [[children.get(root.pk, []), 0, '']]

        while stack:
            frame = stack[-1]
            siblings, index, prefix = frame

            if index >= len(siblings):
                stack.pop()
                continue

            frame[1] += 1
            child = siblings[index]
            is_last = index == len(siblings) - 1
            lines.append(f'{prefix}{"└── " if is_last else "├── "}{child.name}')

            grandchildren = children.get(child.pk)
            if grandchildren:
                stack.append([grandchildren, 0, prefix + ('    ' if is_last else '│   ')])

    return '\n'.join(lines)
