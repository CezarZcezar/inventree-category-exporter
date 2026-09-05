# InvenTree Category Exporter Plugin

A custom plugin for [InvenTree](https://inventree.org) that allows you to easily export the Part Category tree to CSV, XLSX, or a text-based tree format (similar to the Linux `tree` command).

## Features

- **CSV Export:** Download the entire category tree as a CSV file, including hierarchy level and path string.
- **XLSX Export:** Download the category tree as a Microsoft Excel file.
- **Tree Export:** Download a text representation of the category tree showing its hierarchical structure.

## Installation

You can install this plugin directly from this Git repository into your InvenTree instance.

1. Go to the **System Settings** -> **Plugins** page in your InvenTree admin panel.
2. Click on the **Install Plugin** button.
3. In the "Package Name or URL" field, enter the Git URL for this repository (e.g., `git+https://github.com/CezarZcezar/inventree-category-exporter.git`).
4. Click **Install**.
5. Restart your InvenTree server worker to load the new plugin.
6. Once restarted, go back to **System Settings** -> **Plugins** and ensure the **Category Exporter** plugin is checked/enabled.

### Alternative Installation (Docker)

If you are using Docker, you can add the following line to your `plugins.txt` file located in the InvenTree data directory:

```
inventree-category-exporter@git+https://github.com/CezarZcezar/inventree-category-exporter.git
```

Then, restart your containers:

```bash
docker-compose down
docker-compose up -d
```

## Usage

Once the plugin is installed and enabled:

1. Navigate to your InvenTree URL and append `/plugin/category_exporter/` (e.g., `http://your-inventree.local/plugin/category_exporter/`).
2. You will be presented with three download buttons:
   - **Download CSV**
   - **Download XLSX**
   - **Download Tree (TXT)**
3. Click any button to download the respective file.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
