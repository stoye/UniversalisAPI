# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sys, os
import universalisapi
from intersphinx_registry import get_intersphinx_mapping

# add pygments directory
sys.path.append(os.path.abspath("./_pygments"))

project = 'UniversalisAPI'
copyright = '2025, Steve Toye'
author = 'Steve Toye'
release = '0.1.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'numpydoc',
    #"sphinx.ext.napoleon",
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode'
]

templates_path = ['_templates']
exclude_patterns = []

# -- Numpydoc Config ---------------------------------------------------------
numpydoc_xref_param_type = True
numpydoc_xref_ignore = {"optional", "type_without_description", "BadException"}

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "tomorrownight.TomorrownightStyle"
#pygments_style = "sphinx"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_theme_options = {
    "pygments_light_style": "a11y-high-contrast-light",
    "pygments_dark_style": "a11y-dark"
}

# -- Intersphinx setup ----------------------------------------------------

# Example configuration for intersphinx: refer to several Python libraries.

intersphinx_mapping = get_intersphinx_mapping(packages=["python"])
