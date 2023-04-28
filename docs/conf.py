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

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add napoleon to the extensions list
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
master_doc = "index"
autoapi_dirs = ["logml"]
autodoc_default_options = {
    "member-order": "bysource",
    "undoc-members": True,
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']

html_theme_options = {
    "canonical_url": "",
    "analytics_id": "UA-XXXXXXX-1",
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "both",
    "style_external_links": "#ff9900",
    "style_nav_header_background": "#ff9900",
    # Toc options
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}
html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": "valentingol",  # Username
    "github_repo": "LoggerML",  # Repo name
    "github_version": "dev",  # Version
    "conf_py_path": "/docs/",  # Path in the checkout to the docs root
}
