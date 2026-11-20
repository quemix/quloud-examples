# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Quloud Examples'
copyright = '2026, Quemix inc'
author = 'Jun-Ichi Iwata'
version = '2026.5.25'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.mathjax', 'sphinx.ext.githubpages']

templates_path = ['_templates']
exclude_patterns = [
    '_build', 'docs', 'meta', 'tmp', '.claude', 'Thumbs.db', '.DS_Store',
    'li3po4/md-trajectory-energy.rst',
    'li3po4/nnp-input-energy-error.rst',
    'li3po4/structure-energy.rst',
]

language = 'ja'

numfig = True
numfig_secnum_depth = 1

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
# sphinx.ext.githubpages writes CNAME from this domain.
html_baseurl = 'https://example.quloud-platform.quemix.com/'
html_static_path = ['_static']
html_js_files = ['js/language-switcher.js']
html_css_files = ['custom.css']
html_title = 'Quloudの計算事例'
html_short_title = html_title
html_context = {'default_mode': 'light'}
html_sidebars = {'index': []}
html_theme_options = {
    'navbar_center': ['examples-navbar'],
    'navbar_end': ['language-switcher'],
    'footer_start': ['copyright'],
    'footer_end': [],
    'navigation_depth': 2,
    'search_bar_text': '計算事例を検索',
    'secondary_sidebar_items': {'index': [], '**': ['page-toc']},
    'shorten_urls': False,
}

