# -*- coding: utf-8 -*-


import setuptools  # type: ignore

from inventree_rexel.version import REXEL_PLUGIN_VERSION

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setuptools.setup(
    name="inventree-rexel-plugin",

    version=REXEL_PLUGIN_VERSION,

    author="Philip van der honing",

    author_email="philipvanderhoning@gmail.com",

    description="rexel product import plugin for InvenTree",

    long_description=long_description,

    long_description_content_type='text/markdown',

    keywords="inventree rexel product import inventory",

    url="https://github.com/philipboy881/inventree-rexel-plugin",

    license="MIT",

    packages=setuptools.find_packages(),

    install_requires=[
        'tablib',
        'requests',
        'beautifulsoup4',
        'python-dotenv',
    ],

    setup_requires=[
        "wheel",
        "twine",
    ],

    python_requires=">=3.6",

    entry_points={
        "inventree_plugins": [
            "rexelPlugin = inventree_rexel.core:RexelPlugin"
        ]
    },
)
