"""InvenTree Category Exporter plugin."""

import importlib.util

PLUGIN_VERSION = '1.3.0'
__version__ = PLUGIN_VERSION

__all__ = ['PLUGIN_VERSION']

# The plugin class can only be imported inside an InvenTree environment.
# Outside of it (e.g. running the unit tests) only the export logic is usable.
if importlib.util.find_spec('InvenTree') is not None:
    from .plugin import CategoryExporterPlugin  # noqa: E402,F401

    __all__.append('CategoryExporterPlugin')
