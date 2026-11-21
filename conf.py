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

import os
import sys

sys.path.insert(0, os.path.abspath('_ext'))

extensions = ['sphinx.ext.mathjax', 'sphinx.ext.githubpages', 'cjk_linebreak']

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
    'article_header_start': ['breadcrumbs', 'case-links'],
    'article_footer_items': ['case-end'],
    'footer_start': ['copyright'],
    'footer_end': [],
    'navigation_depth': 2,
    'search_bar_text': '計算事例を検索',
    'secondary_sidebar_items': {'index': [], '**': ['page-toc']},
    'shorten_urls': False,
}


def configure_case_navigation(app, pagename, _templatename, context, _doctree):
    if pagename == app.config.root_doc:
        context['theme_article_header_start'] = []

    case_dir = pagename.partition('/')[0]
    case_index = f'{case_dir}/index'
    toctree = app.env.toctree_includes
    case_indexes = toctree.get(app.config.root_doc, ())
    case_pages = toctree.get(case_index, ()) if case_index in case_indexes else ()
    related = app.builder.relations.get(pagename, (None, None, None))
    in_case = pagename == case_index or pagename in case_pages

    for key, target in zip(('prev', 'next'), related[1:]):
        if not in_case or (target != case_index and target not in case_pages):
            context[key] = None
            context['rellinks'] = [
                link for link in context.get('rellinks', ()) if link[0] != target
            ]
    context['theme_show_prev_next'] = bool(context.get('prev') or context.get('next'))

    # The sidebar title (e.g. 「CO₂の赤外スペクトル目次」) links to the case's top page.
    if case_index in case_indexes and case_index in app.env.titles:
        context['case_title'] = app.env.titles[case_index].astext()
        context['case_url'] = context['pathto'](case_index)

    if pagename not in case_pages:
        return

    context['case_end'] = pagename == case_pages[-1]
    reproduction = f'{case_dir}/reproduction'
    if pagename == reproduction:
        result_pages = [page for page in case_pages if page != reproduction]
        context['case_results'] = [
            (page, '計算結果に戻る' if len(result_pages) == 1 else app.env.titles[page].astext())
            for page in result_pages
        ]
    elif reproduction in case_pages:
        context['case_reproduction'] = reproduction


def setup(app):
    app.connect('html-page-context', configure_case_navigation, priority=400)
