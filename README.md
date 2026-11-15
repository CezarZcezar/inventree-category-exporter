# InvenTree Category Exporter Plugin

[![InvenTree Plugin](https://img.shields.io/badge/InvenTree-Plugin-blue.svg)](https://inventree.org)
[![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A custom plugin for [InvenTree](https://inventree.org) that allows you to easily export the complete Part Category tree to **CSV**, **XLSX**, or a text-based tree format (similar to the Linux `tree` command).

---

## Features

- **Panel in the Parts page:** a *Categories Tree* panel is shown in the left-hand panel list of the Parts page (next to *Part Categories* and *Parts*) and on every part category page. It displays the category tree as text (with a copy button) and offers the downloads.
- **Sub-tree export:** on a category page you can export only that category and its subcategories, or all categories.
- **CSV / XLSX export** with the same information as the category table in InvenTree:
  ID, Name, Path, Level, Description, Parent Category (ID), Default Location, Parent Default Location,
  Default Keywords, Parts (including subcategories), Subcategories (all levels), Structural,
  Starred (by the user who downloads the file) and Icon. Locations are written as their full path.
  Values which a spreadsheet would run as a formula (`=`, `+`, `-`, `@`) are prefixed with `'`.
- **Tree export:** a text tree like the Linux `tree` command (`├──`, `└──`).
- **Permissions:** you must be logged in and have the *Part Categories: View* role.

Requires InvenTree 1.0+ (React UI) with **Settings → Plugins → Enable interface integration** and **Enable URL integration** turned on.

---

## Installation

### Local Docker deployment

```bash
./deploy.sh            # copies the plugin to ../inventree-data/plugins/category_exporter and restarts InvenTree
```

### Via Git / `plugins.txt`

```
inventree-category-exporter@git+https://github.com/CezarZcezar/inventree-category-exporter.git
```

Then activate the plugin under **Settings → Plugins**.

---

## Usage

Open **Parts** and select the **Categories Tree** panel. The tree is shown right away; use the CSV / XLSX / TXT buttons to download it.

The downloads can also be used directly (for scripts):

| URL | Result |
|-----|--------|
| `/plugin/category_exporter/export/csv/` | CSV |
| `/plugin/category_exporter/export/xlsx/` | XLSX |
| `/plugin/category_exporter/export/tree/` | text tree (download) |
| `/plugin/category_exporter/tree/` | text tree (inline, used by the panel) |

Add `?category=<id>` to export only one category and its subcategories.
`/plugin/category_exporter/` still shows a simple standalone page with the links.

---

## Tests

The export logic has no InvenTree dependency and is tested on its own:

```bash
python -m unittest discover -s tests -v
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
