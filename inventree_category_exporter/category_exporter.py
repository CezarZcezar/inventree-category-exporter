"""InvenTree plugin for exporting Part Categories to CSV, XLSX, and text tree formats."""

import datetime
from typing import List

try:
    from django.http import HttpResponse
    from django.urls import path
except ImportError:  # pragma: no cover
    path = lambda *args, **kwargs: None

    class HttpResponse:
        """Fallback dummy HttpResponse for testing environments without Django."""

        def __init__(self, content="", content_type="text/plain; charset=utf-8"):
            self.content = content
            self.content_type = content_type
            self.headers = {}

        def __setitem__(self, key, value):
            self.headers[key] = value

        def __getitem__(self, key):
            return self.headers.get(key)


try:
    from plugin import InvenTreePlugin
    from plugin.mixins import UrlsMixin
except ImportError:  # pragma: no cover
    class InvenTreePlugin:
        pass

    class UrlsMixin:
        pass


try:
    from part.models import PartCategory
except ImportError:  # pragma: no cover
    PartCategory = None

try:
    import tablib
except ImportError:  # pragma: no cover
    tablib = None


def build_category_tree(categories: List) -> str:
    """Build a visual ASCII/Unicode tree representation from category items."""
    children_dict = {}
    roots = []

    for c in categories:
        parent_id = getattr(c, 'parent_id', None)
        if parent_id:
            children_dict.setdefault(parent_id, []).append(c)
        else:
            roots.append(c)

    lines = []

    def print_tree(node, prefix=""):
        node_pk = getattr(node, 'pk', getattr(node, 'id', None))
        children = children_dict.get(node_pk, [])
        for i, child in enumerate(children):
            is_last = (i == len(children) - 1)
            marker = "└── " if is_last else "├── "
            lines.append(f"{prefix}{marker}{getattr(child, 'name', '')}")
            extension = "    " if is_last else "│   "
            print_tree(child, prefix + extension)

    for root in roots:
        lines.append(getattr(root, 'name', ''))
        print_tree(root, "")

    return '\n'.join(lines)


class CategoryExporterPlugin(UrlsMixin, InvenTreePlugin):
    """A simple plugin to export Part Categories to CSV, XLSX and Tree format."""

    NAME = "CategoryExporterPlugin"
    SLUG = "category_exporter"
    TITLE = "Category Exporter"
    DESCRIPTION = "Export part categories to CSV, XLSX, or tree format."
    VERSION = "1.0.0"
    AUTHOR = "AI Assistant"

    def setup_urls(self):
        """Setup URL endpoints for this plugin."""
        return [
            path('export/csv/', self.export_csv, name='export-csv'),
            path('export/xlsx/', self.export_xlsx, name='export-xlsx'),
            path('export/tree/', self.export_tree, name='export-tree'),
            path('', self.index_view, name='index'),
        ]

    def _get_categories(self):
        """Retrieve categories ordered by MPTT tree_id and lft."""
        if PartCategory:
            return PartCategory.objects.all().order_by('tree_id', 'lft')
        return []

    def _generate_dataset(self, categories=None):
        """Generate a tablib Dataset of categories."""
        if tablib is None:
            raise RuntimeError("tablib library is required for dataset generation")

        if categories is None:
            categories = self._get_categories()

        dataset = tablib.Dataset()
        dataset.headers = ['ID', 'Name', 'Path', 'Level', 'Description']

        for category in categories:
            dataset.append([
                getattr(category, 'pk', getattr(category, 'id', None)),
                getattr(category, 'name', ''),
                getattr(category, 'pathstring', ''),
                getattr(category, 'level', 0),
                getattr(category, 'description', '') or '',
            ])
        return dataset

    def export_csv(self, request=None, categories=None):
        """Export categories to CSV HTTP response."""
        dataset = self._generate_dataset(categories)
        response = HttpResponse(dataset.csv, content_type='text/csv')
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        response['Content-Disposition'] = f'attachment; filename="categories_{date_str}.csv"'
        return response

    def export_xlsx(self, request=None, categories=None):
        """Export categories to Excel XLSX HTTP response."""
        dataset = self._generate_dataset(categories)
        response = HttpResponse(
            dataset.xlsx,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        response['Content-Disposition'] = f'attachment; filename="categories_{date_str}.xlsx"'
        return response

    def export_tree(self, request=None, categories=None):
        """Export categories to ASCII/Unicode text tree HTTP response."""
        if categories is None:
            categories = self._get_categories()

        tree_text = build_category_tree(categories)
        response = HttpResponse(tree_text, content_type='text/plain; charset=utf-8')
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        response['Content-Disposition'] = f'attachment; filename="categories_tree_{date_str}.txt"'
        return response

    def index_view(self, request=None):
        """HTML view providing download links for each export format."""
        html = """
        <html>
        <head>
            <title>Category Exporter</title>
            <style>
                body { font-family: sans-serif; padding: 2rem; }
                .btn { display: inline-block; padding: 10px 20px; margin: 10px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; }
                .btn:hover { background-color: #0056b3; }
            </style>
        </head>
        <body>
            <h1>InvenTree Category Exporter</h1>
            <p>Select a format to download the Part Category tree:</p>
            <a class="btn" href="export/csv/">Download CSV</a>
            <a class="btn" href="export/xlsx/">Download XLSX</a>
            <a class="btn" href="export/tree/">Download Tree (TXT)</a>
        </body>
        </html>
        """
        return HttpResponse(html, content_type='text/html')
