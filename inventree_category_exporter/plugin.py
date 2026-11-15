"""Category Exporter plugin for InvenTree.

Exports the Part Category tree to CSV, XLSX or a text tree and adds a
"Categories Tree" panel to the Parts page (and to every part category page).
"""

from __future__ import annotations

from django.urls import path
from django.utils.translation import gettext_lazy as _

from plugin import InvenTreePlugin
from plugin.mixins import UrlsMixin, UserInterfaceMixin

from . import PLUGIN_VERSION, views


class CategoryExporterPlugin(UserInterfaceMixin, UrlsMixin, InvenTreePlugin):
    """Export part categories to CSV, XLSX or a text tree."""

    NAME = 'CategoryExporterPlugin'
    SLUG = 'category_exporter'
    TITLE = _('Category Exporter')
    DESCRIPTION = _('Export part categories to CSV, XLSX, or tree format')
    VERSION = PLUGIN_VERSION
    AUTHOR = 'Cezary Ćwikowski'
    PUBLISH_DATE = '2026-11-15'
    WEBSITE = 'https://github.com/CezarZcezar/inventree-category-exporter'
    LICENSE = 'MIT'
    MIN_VERSION = '1.0.0'

    def setup_urls(self):
        """URL endpoints of the plugin (mounted at /plugin/category_exporter/)."""
        return [
            path('export/<str:fmt>/', views.export_view, name='export'),
            path('tree/', views.tree_view, name='tree'),
            path('ui/<str:tag>/category_exporter.js', views.panel_script_view, name='panel-js'),
            path('', views.index_view, name='index'),
        ]

    @property
    def plugin_url(self) -> str:
        """Absolute URL prefix of the plugin endpoints, e.g. /plugin/category_exporter/."""
        return '/' + self.base_url.strip('/') + '/'

    def get_ui_panels(self, request, context: dict, **kwargs):
        """Add the export panel to the Parts index and part category pages."""
        if context.get('target_model') != 'partcategory':
            return []

        if not views.has_permission(getattr(request, 'user', None)):
            return []

        # No target_id on the Parts index page (top level), otherwise the category pk
        try:
            category_id = int(context.get('target_id'))
        except (TypeError, ValueError):
            category_id = None

        return [
            {
                'key': 'category-exporter',
                'title': _('Categories Tree'),
                'description': _('Part category tree, with CSV / XLSX / text export'),
                'icon': 'ti:binary-tree:outline',
                # Served through Django (see views.panel_script_view), so no
                # 'collectplugins' step is needed and it works behind any proxy
                'source': f'{self.plugin_url}ui/{views.panel_script_tag()}/category_exporter.js:renderPanel',
                'context': {
                    'base_url': self.plugin_url,
                    'category_id': category_id,
                    'version': self.VERSION,
                },
            }
        ]
