import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="inventree-category-exporter",
    version="1.0.0",
    author="Cezary",
    author_email="cwikowski.czarek123@gmail.com",
    description="An InvenTree plugin to export Part Categories to CSV, XLSX, and Tree formats.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YourUsername/inventree-category-exporter",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "tablib",
    ],
    entry_points={
        "inventree_plugins": [
            "CategoryExporterPlugin = inventree_category_exporter.category_exporter:CategoryExporterPlugin",
        ]
    },
)
