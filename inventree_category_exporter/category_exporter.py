from django.urls import path
from django.http import HttpResponse

from plugin import InvenTreePlugin
from plugin.mixins import UrlsMixin

from part.models import PartCategory
import tablib
import datetime

class CategoryExporterPlugin(UrlsMixin, InvenTreePlugin):
    """
    A simple plugin to export Part Categories to CSV, XLSX and Tree format.
    """
    
    NAME = "CategoryExporterPlugin"
    SLUG = "category_exporter"
    TITLE = "Category Exporter"
    DESCRIPTION = "Export part categories to CSV, XLSX, or tree format."
    VERSION = "1.0.0"
    AUTHOR = "AI Assistant"

    def setup_urls(self):
        """
        Setup URL endpoints for this plugin
        """
        return [
            path('export/csv/', self.export_csv, name='export-csv'),
            path('export/xlsx/', self.export_xlsx, name='export-xlsx'),
            path('export/tree/', self.export_tree, name='export-tree'),
            path('', self.index_view, name='index'),
        ]

    def _get_categories(self):
        # MPTT models have tree_id and lft which guarantees a pre-order depth-first traversal (tree order)
        return PartCategory.objects.all().order_by('tree_id', 'lft')

    def _generate_dataset(self):
        dataset = tablib.Dataset()
        dataset.headers = ['ID', 'Name', 'Path', 'Level', 'Description']
        
        for category in self._get_categories():
            dataset.append([
                category.pk,
                category.name,
                category.pathstring,
                category.level,
                category.description,
            ])
        return dataset

    def export_csv(self, request):
        dataset = self._generate_dataset()
        response = HttpResponse(dataset.csv, content_type='text/csv')
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        response['Content-Disposition'] = f'attachment; filename="categories_{date_str}.csv"'
        return response

    def export_xlsx(self, request):
        dataset = self._generate_dataset()
        response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        response['Content-Disposition'] = f'attachment; filename="categories_{date_str}.xlsx"'
        return response

    def export_tree(self, request):
        categories = self._get_categories()
        
        # Build children mapping
        children_dict = {}
        roots = []
        for c in categories:
            if c.parent_id:
                children_dict.setdefault(c.parent_id, []).append(c)
            else:
                roots.append(c)
                
        lines = []
        
        def print_tree(node, prefix=""):
            children = children_dict.get(node.pk, [])
            for i, child in enumerate(children):
                is_last = (i == len(children) - 1)
                marker = "└── " if is_last else "├── "
                lines.append(f"{prefix}{marker}{child.name}")
                extension = "    " if is_last else "│   "
                print_tree(child, prefix + extension)
                
        for root in roots:
            lines.append(root.name)
            print_tree(root, "")
            
        response = HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        response['Content-Disposition'] = f'attachment; filename="categories_tree_{date_str}.txt"'
        return response
        
    def index_view(self, request):
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
        return HttpResponse(html)
