# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os, sys, pathlib
HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[2]            # repo-root (tilpass hvis struktur avviker)
SRC  = ROOT / "src"               # hvis du har "src"-layout
for p in (ROOT, SRC):
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

try:
    import hdlregression
    release = hdlregression.__version__
except Exception:
    # Fallback: les versjon manuelt hvis import fortsatt feiler
    release = os.environ.get("HDLREGRESSION_VERSION", "0.0.0")

# -- Project information -----------------------------------------------------

project = 'hdlregression'
copyright = '2021, UVVM'
author = 'UVVM'
#release = hdlregression.__version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autosectionlabel',
]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = 'images/hdlregression_scaled.png'

html_theme_options = {
    'navigation_depth': '3',
    'style_nav_header_background': '#F5F5F5',
    'logo_only': 'True',
    'display_version': False,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".

