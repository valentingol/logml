"""Configuration file for the Sphinx documentation builder."""
# pylint: disable=all
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

from setuptools_scm import get_version

sys.path.insert(0, os.path.abspath('../'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'LoggerML'
copyright = '2023, Valentin Goldite'  # noqa A001
author = 'Valentin Goldite'
try:
    release = get_version()
except:  # noqa E722
    release = get_version(root='..', relative_to=__file__)
release = ".".join(release.split(".")[:3]) + ".dev" if "dev" in release else ""

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
]

master_doc = "index"
autoapi_type = 'python'
autoapi_dirs = ["logml"]

autodoc_default_options = {
    "member-order": "bysource",
    "undoc-members": True,
}

add_module_names = False
autoclass_content = "both"
napoleon_use_param = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/", None),
    "numpy": ("http://docs.scipy.org/doc/numpy/", None),
}

templates_path = ['_templates']
exclude_patterns = ['_build']

rst_prolog = """
.. |default| raw:: html

    <div class="default-value-section">""" + \
    ' <span class="default-value-label">Default:</span>'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
html_css_files = ["custom.css"]

html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": "valentingol",  # Username
    "github_repo": "LoggerML",  # Repo name
    "github_version": "main",  # Version
    "conf_py_path": "/docs/",  # Path in the checkout to the docs root
}
