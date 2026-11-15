import re
from pathlib import Path

import setuptools

HERE = Path(__file__).parent

long_description = (HERE / 'README.md').read_text(encoding='utf-8')
version = re.search(
    r"PLUGIN_VERSION = '([^']+)'",
    (HERE / 'inventree_category_exporter' / '__init__.py').read_text(encoding='utf-8'),
).group(1)

setuptools.setup(
    name='inventree-category-exporter',
    version=version,
    author='Cezary Ćwikowski',
    author_email='cwikowski.czarek123@gmail.com',
    description='An InvenTree plugin to export Part Categories to CSV, XLSX and text tree formats.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/CezarZcezar/inventree-category-exporter',
    license='MIT',
    keywords=['inventree', 'plugin', 'export', 'categories'],
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    package_data={'inventree_category_exporter': ['static/*.js']},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: InvenTree',
    ],
    python_requires='>=3.10',
    # tablib (with xlsx support) is already shipped with InvenTree
    install_requires=[],
    entry_points={
        'inventree_plugins': [
            'CategoryExporterPlugin = inventree_category_exporter.plugin:CategoryExporterPlugin',
        ]
    },
)
