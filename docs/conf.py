"""
Sphinx configuration for Scientific Voyager documentation.
"""

import os
import sys
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.abspath('..'))

# Project information
project = 'Scientific Voyager'
copyright = f'{datetime.now().year}, Scientific Voyager Contributors'
author = 'Scientific Voyager Contributors'
version = '0.1.0'
release = '0.1.0'

# Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.todo',
    'sphinx_rtd_theme',
]

# Configuration options
autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
napoleon_google_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
todo_include_todos = True

# Templates
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_title = 'Scientific Voyager Documentation'
html_logo = None
html_favicon = None
html_show_sourcelink = True
html_show_sphinx = True
html_show_copyright = True

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),
}
