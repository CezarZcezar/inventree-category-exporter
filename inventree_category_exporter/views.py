"""HTTP views of the Category Exporter plugin."""

from __future__ import annotations

from html import escape
from pathlib import Path

from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.http import require_GET

from .exporter import build_category_tree, build_dataset

PANEL_SCRIPT = Path(__file__).parent / 'static' / 'category_exporter.js'

FORMATS = {
    'csv': ('text/csv; charset=utf-8', 'csv'),
    'xlsx': ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'xlsx'),
    'tree': ('text/plain; charset=utf-8', 'txt'),
}


def has_permission(user) -> bool:
    """The user must be logged in and have the 'part_category: view' role."""
    from users.permissions import check_user_role

    return bool(user and user.is_authenticated and check_user_role(user, 'part_category', 'view'))


def get_categories(category_id=None, annotate: bool = True):
    """Return the categories in tree order, optionally only the sub-tree of one category.

    Annotated like the InvenTree API (part_count, subcategories, parent_default_location),
    so the numbers match the category table in the web UI.
    """
    from part.models import PartCategory
    from part.serializers import CategorySerializer

    if category_id in (None, ''):
        queryset = PartCategory.objects.all()
    else:
        try:
            root = PartCategory.objects.get(pk=int(category_id))
        except (ValueError, TypeError, PartCategory.DoesNotExist):
            raise Http404('Category not found')

        queryset = root.get_descendants(include_self=True)

    if annotate:
        queryset = CategorySerializer.annotate_queryset(queryset)

    return list(queryset.order_by('tree_id', 'lft'))


def get_location_paths(categories) -> dict:
    """Map pk -> path of all stock locations referenced by the categories (one query)."""
    from stock.models import StockLocation

    ids = set()
    for category in categories:
        ids.update(filter(None, (category.default_location_id, category.parent_default_location)))

    if not ids:
        return {}

    return dict(StockLocation.objects.filter(pk__in=ids).values_list('pk', 'pathstring'))


def get_parent_names(categories) -> dict:
    """Map pk -> name of parents which are not in the exported list (one query, sub-tree exports)."""
    from part.models import PartCategory

    known = {category.pk for category in categories}
    ids = {category.parent_id for category in categories if category.parent_id and category.parent_id not in known}

    if not ids:
        return {}

    return dict(PartCategory.objects.filter(pk__in=ids).values_list('pk', 'name'))


def get_starred(user) -> set:
    """Return the pks of the categories directly starred by the user."""
    return set(user.starred_categories.values_list('category_id', flat=True))


def export_filename(extension: str, suffix: str = '') -> str:
    """Return e.g. categories_2026-11-15.csv."""
    date = timezone.localdate().isoformat()
    return f'categories{suffix}_{date}.{extension}'


@require_GET
def export_view(request, fmt: str):
    """Download the categories (?category=<pk> limits the export to a sub-tree)."""
    if not has_permission(request.user):
        return HttpResponseForbidden('Insufficient permissions (part category: view)')

    if fmt not in FORMATS:
        raise Http404('Unknown export format')

    content_type, extension = FORMATS[fmt]
    # The text tree needs no part / location counts
    categories = get_categories(request.GET.get('category'), annotate=fmt != 'tree')

    if fmt == 'tree':
        content = build_category_tree(categories) + '\n'
        filename = export_filename(extension, '_tree')
    else:
        dataset = build_dataset(
            categories, get_location_paths(categories), get_starred(request.user), get_parent_names(categories)
        )
        content = dataset.export(fmt)
        filename = export_filename(extension)

    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@require_GET
def tree_view(request):
    """Return the text tree inline (shown in the panel), ?category=<pk> for a sub-tree."""
    if not has_permission(request.user):
        return HttpResponseForbidden('Insufficient permissions (part category: view)')

    categories = get_categories(request.GET.get('category'), annotate=False)
    response = HttpResponse(build_category_tree(categories), content_type='text/plain; charset=utf-8')
    response['Cache-Control'] = 'no-store'
    return response


@require_GET
def index_view(request):
    """Standalone page with download links (the panel in the Parts page is preferred)."""
    if not has_permission(request.user):
        return HttpResponseForbidden('Insufficient permissions (part category: view)')

    links = ''.join(
        f'<a class="btn" href="export/{fmt}/">{escape(label)}</a>'
        for fmt, label in (('csv', 'Download CSV'), ('xlsx', 'Download XLSX'), ('tree', 'Download Tree (TXT)'))
    )

    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Category Exporter</title>
<style>
body {{ font-family: sans-serif; padding: 2rem; }}
.btn {{ display: inline-block; padding: 10px 20px; margin: 10px; background: #228be6; color: #fff;
        text-decoration: none; border-radius: 5px; }}
.btn:hover {{ background: #1c7ed6; }}
</style>
</head>
<body>
<h1>InvenTree Category Exporter</h1>
<p>Select a format to download the Part Category tree:</p>
{links}
</body>
</html>"""
    return HttpResponse(html, content_type='text/html; charset=utf-8')


def panel_script_tag() -> str:
    """Cache-busting tag for the panel script URL (changes whenever the file changes)."""
    try:
        stat = PANEL_SCRIPT.stat()
        return f'{int(stat.st_mtime)}-{stat.st_size}'
    except OSError:
        return '0'


@require_GET
def panel_script_view(request, tag: str):
    """Serve the panel JavaScript module (contains no sensitive data)."""
    try:
        content = PANEL_SCRIPT.read_text(encoding='utf-8')
    except OSError:
        raise Http404('Panel script not found')

    response = HttpResponse(content, content_type='text/javascript; charset=utf-8')
    # The URL contains a version tag, so the module can be cached
    response['Cache-Control'] = 'public, max-age=86400'
    response['X-Content-Type-Options'] = 'nosniff'
    return response
