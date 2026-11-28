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

# cjk_linebreak: 日本語の文の途中で改行した原稿で、表示に空白が入らないようにする。
# english_edition: 英語版（locales/en/published.txt のページ）と日本語版を相互にリンクし、未訳のページは原文への案内にする。
# partner_links: 英語版で、技術ノートへのリンクを技術ノートの英語版へ向ける（英語版のあるページだけ）。
extensions = [
    'sphinx.ext.mathjax', 'sphinx.ext.githubpages', 'cjk_linebreak', 'english_edition',
    'partner_links',
]

templates_path = ['_templates']
exclude_patterns = [
    '_build', 'docs', 'meta', 'tmp', '.claude', 'Thumbs.db', '.DS_Store',
    'li3po4/md-trajectory-energy.rst',
    'li3po4/nnp-input-energy-error.rst',
    'li3po4/structure-energy.rst',
]

language = os.environ.get('QULOUD_DOC_LANGUAGE', 'ja')
locale_dirs = ['locales/']
gettext_compact = False
# 日本語の原文が少し変わった文は、訳し直すまで前の英訳を出す（英語のページに日本語の段落を混ぜない）。
# 古い訳の残るページには english_edition が注記を出し、ビルドで警告する。
gettext_allow_fuzzy_translations = True
# コードブロックも翻訳の対象にし、英語版ではコメントを英語にする。
gettext_additional_targets = ['literal-block']

numfig = True
numfig_secnum_depth = 1

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
# sphinx.ext.githubpages writes CNAME from this domain.
quloud_japanese_baseurl = 'https://example.quloud-platform.quemix.com/'
quloud_english_baseurl = quloud_japanese_baseurl + 'en/'
# canonical のURLもここから作るので、英語版は /en/ を指す。
html_baseurl = quloud_english_baseurl if language == 'en' else quloud_japanese_baseurl
# 技術ノートの英語版で公開しているページの一覧（partner_links）。
quloud_partner_sites = {
    'https://technical-notes.quemix.com/': 'https://technical-notes.quemix.com/en/published.json',
}
html_static_path = ['_static']
html_js_files = ['js/language-switcher.js']
html_css_files = ['custom.css', 'language-switcher.css']
html_title = 'Quloud Calculation Examples' if language == 'en' else 'Quloudの計算事例'
html_short_title = html_title
html_context = {'default_mode': 'light'}
html_sidebars = {'index': []}
html_theme_options = {
    'navbar_center': ['examples-navbar'],
    'navbar_end': ['theme-switcher', 'language-switcher'],
    'article_header_start': ['breadcrumbs', 'case-links'],
    'article_footer_items': ['case-end'],
    'footer_start': ['copyright'],
    'footer_end': [],
    'navigation_depth': 2,
    'search_bar_text': 'Search Calculation Examples' if language == 'en' else '計算事例を検索',
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
        back = 'Back to Results' if app.config.language == 'en' else '計算結果に戻る'
        context['case_results'] = [
            (page, back if len(result_pages) == 1 else app.env.titles[page].astext())
            for page in result_pages
        ]
    elif reproduction in case_pages:
        context['case_reproduction'] = reproduction


def localize_navigation(app, env):
    """Use fixed labels for links to pages outside the translated catalogs."""
    if app.config.language != 'en' or app.builder.name != 'html':
        return

    import json
    from pathlib import Path

    from docutils import nodes

    label_path = Path(app.confdir) / '_static/translations/en.json'
    labels = json.loads(label_path.read_text(encoding='utf-8'))

    def localize(node):
        key = ' '.join(node.astext().split())
        label = labels.get(key)
        if label:
            node[:] = [nodes.Text(label)]

    for docname, title in env.titles.items():
        # Keep each page's own long title independent of its navigation link.
        title = title.deepcopy()
        localize(title)
        env.titles[docname] = title

    for toc in env.tocs.values():
        for link in toc.findall(nodes.reference):
            if not link.get('anchorname'):
                localize(link)


def setup(app):
    app.connect('env-updated', localize_navigation)
    app.connect('html-page-context', configure_case_navigation, priority=400)
