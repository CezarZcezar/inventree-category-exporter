# InvenTree Category Exporter Plugin

[![InvenTree Plugin](https://img.shields.io/badge/InvenTree-Plugin-blue.svg)](https://inventree.org)
[![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A custom plugin for [InvenTree](https://inventree.org) that allows you to easily export the complete Part Category tree to **CSV**, **XLSX**, or a text-based tree format (similar to the Linux `tree` command).

---

## Features

- **CSV Export:** Download the entire category tree as a CSV file, including ID, Name, Category Path string, Hierarchy Level, and Description.
- **XLSX Export:** Download the category tree as a Microsoft Excel spreadsheet.
- **Tree Export:** Download a visual Unicode/ASCII text representation showing the hierarchical tree structure (using `├──` and `└──`).
- **Web UI & Direct Endpoints:** Download directly through the interactive web view (`/plugin/category_exporter/`) or script downloads via dedicated REST-like download URLs.
- **Automated Tests:** Includes a dedicated test suite with 100% isolated unit tests covering tree construction, datasets, and HTTP responses.

---

## Installation

### Method 1: Local Docker Volume (Recommended)

InvenTree Docker instances automatically load plugins located in the persistent data volume:

1. Copy the plugin files into your `inventree-data/plugins/` directory:
   ```bash
   mkdir -p inventree-data/plugins/category_exporter
   cp -r inventree-category-exporter/inventree_category_exporter/* inventree-data/plugins/category_exporter/
   ```

2. Restart your InvenTree containers:
   ```bash
   docker compose restart inventree-server inventree-worker
   ```

### Method 2: Via Git / `plugins.txt`

Add the Git repository URL to your `inventree-data/plugins.txt`:
```
inventree-category-exporter@git+https://github.com/CezarZcezar/inventree-category-exporter.git
```

Then reload plugins in InvenTree.

---

## Usage

Once the plugin is installed and active:

1. Open your browser and navigate to:
   ```
   http://<your-inventree-url>/plugin/category_exporter/
   ```
2. You will see the Category Exporter interface with three download buttons:
   - **Download CSV** (`/plugin/category_exporter/export/csv/`)
   - **Download XLSX** (`/plugin/category_exporter/export/xlsx/`)
   - **Download Tree (TXT)** (`/plugin/category_exporter/export/tree/`)
3. Click any button to download the category tree file.

---

## Automated Tests

The plugin includes isolated unit tests that verify tree recursion, tablib dataset building, HTTP response headers, and view endpoints without touching the database:

```bash
# Run tests inside the Docker container
docker exec -e PYTHONPATH=/home/inventree/data/plugins/category_exporter inventree-server python3 -m unittest discover -s /home/inventree/data/plugins/category_exporter/tests
```

All 11 tests run in under 0.2 seconds.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
