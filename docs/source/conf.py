"""Configuration file for the Sphinx documentation builder."""

# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import re
from importlib import metadata

from sphinx_gallery.sorting import ExampleTitleSortKey  # pylint: disable=import-error

# -- Project information -----------------------------------------------------

project = "NeuroTS"

# The short X.Y version
version = metadata.version("NeuroTS")

# The full version, including alpha/beta/rc tags
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx_gallery.gen_gallery",
    "sphinx-jsonschema",
    "m2r2",
]

todo_include_todos = True

# Add any paths that contain templates here, relative to this directory.
# templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx-bluebrain-theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

html_theme_options = {
    "metadata_distribution": "NeuroTS",
}

html_title = project

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False

# autosummary settings
autosummary_generate = True

# autodoc settings
autodoc_typehints = "signature"
autodoc_default_options = {"members": True, "show-inheritance": True, "private-members": True}
default_role = "py:obj"
intersphinx_mapping = {
    "morphio": ("https://morphio.readthedocs.io/en/latest/", None),
    "neurom": ("https://neurom.readthedocs.io/en/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "python": ("https://docs.python.org/3", None),
}

sphinx_gallery_conf = {
    "download_all_examples": False,
    "examples_dirs": "../../examples",
    "gallery_dirs": "examples",
    "line_numbers": True,
    "min_reported_time": 999,
    "plot_gallery": False,
    "within_subsection_order": ExampleTitleSortKey,
}


def fix_signature(app, what, name, obj, options, signature, return_annotation):
    """Remove the module locations from signatures."""
    # pylint: disable=unused-argument
    if signature:
        module_pattern = r"(.*)<module '(.*)' from '.*'>(.*)"
        match = re.match(module_pattern, signature)
        if match:
            return "".join(match.groups()), return_annotation

    return None


def setup(app):
    """Setup Sphinx by connecting functions to events."""
    app.connect("autodoc-process-signature", fix_signature)
