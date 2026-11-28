"""Link the Japanese site and its English edition built from the same sources.

Only the articles listed in ``locales/en/published.txt`` are published in English.
The English build keeps every other page (so that the toctree, the cross references
and the volume numbering stay the same as in Japanese) but replaces its body with a
link to the Japanese original. A published article whose catalog has fuzzy or
missing translations gets a notice at the top and a build warning.
"""

import json
import re
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst.directives.misc import Raw
from sphinx.util import logging

logger = logging.getLogger(__name__)

PUBLISHED_LIST = 'locales/en/published.txt'
JAPANESE_TEXT = re.compile(r'[\u3040-\u30ff\u3400-\u9fff]')


class TranslatableRaw(Raw):
    """Opt a raw block with reader-facing text into Sphinx gettext."""

    def run(self):
        raw_nodes = super().run()
        for node in raw_nodes:
            if isinstance(node, nodes.raw):
                node['translatable'] = True
        return raw_nodes


def read_published(confdir):
    """Return the docnames listed in PUBLISHED_LIST (``#`` starts a comment)."""
    path = Path(confdir) / PUBLISHED_LIST
    if not path.exists():
        return set()
    lines = path.read_text(encoding='utf-8').splitlines()
    return {line.split('#', 1)[0].strip() for line in lines} - {''}


def _japanese_url(pagename):
    """Relative URL from an English page (under en/) to the same Japanese page."""
    return '../' * (pagename.count('/') + 1) + pagename + '.html'


def _english_url(pagename):
    """Relative URL from a Japanese page to the same English page."""
    return '../' * pagename.count('/') + 'en/' + pagename + '.html'


def _catalog_status(app, docname):
    """Count fuzzy and untranslated messages in the article's catalog."""
    from babel.messages.pofile import read_po

    path = Path(app.confdir) / 'locales/en/LC_MESSAGES' / f'{docname}.po'
    if not path.exists():
        return None
    with path.open('rb') as f:
        catalog = read_po(f)
    messages = [m for m in catalog if m.id]
    return {
        'fuzzy': sum(1 for m in messages if m.fuzzy),
        'untranslated': sum(1 for m in messages if not m.string),
    }


def _japanese_paragraphs(doctree):
    """Count text blocks left in Japanese, outside the toctree lists of other pages."""
    count = 0
    for block in doctree.findall(nodes.TextElement):
        if any('toctree-wrapper' in a.get('classes', []) for a in _ancestors(block)):
            continue
        # Comments and substitution definitions are not displayed. Sphinx translates
        # a heading written as |name| at the substitution reference.
        if isinstance(block, (nodes.literal_block, nodes.math_block, nodes.raw,
                              nodes.comment, nodes.substitution_definition)):
            continue
        own_text = ''.join(t.astext() for t in block.children if isinstance(t, nodes.Text))
        if JAPANESE_TEXT.search(own_text):
            count += 1
    return count


def _ancestors(node):
    node = node.parent
    while node is not None:
        yield node
        node = node.parent


def _notice(text, classes, link_text=None, refuri=None, after=''):
    """A notice: text, then an optional link to the Japanese original, then more text."""
    paragraph = nodes.paragraph()
    paragraph += nodes.Text(text)
    if link_text:
        paragraph += nodes.Text(' ')
        paragraph += nodes.reference('', link_text, refuri=refuri, internal=False)
        paragraph += nodes.Text('.')
    if after:
        paragraph += nodes.Text(' ' + after)
    return nodes.container('', paragraph, classes=['quloud-edition-notice', *classes])


def _kept_anchors(ids):
    """Empty anchors for the ids of a replaced page body, and a script that carries the
    followed anchor over to the link to the Japanese original (the same ids exist there)."""
    spans = ''.join(f'<span id="{i}" class="quloud-kept-anchor"></span>' for i in dict.fromkeys(ids))
    script = (
        '<script>(() => {\n'
        '  const follow = () => {\n'
        '    const id = decodeURIComponent(location.hash.slice(1));\n'
        '    const target = id && document.getElementById(id);\n'
        '    const link = document.querySelector(".quloud-edition-untranslated a.reference");\n'
        '    if (link) {\n'
        '      const kept = target && target.classList.contains("quloud-kept-anchor");\n'
        '      link.hash = kept ? location.hash : "";\n'
        '    }\n'
        '  };\n'
        '  follow();\n'
        '  window.addEventListener("hashchange", follow);\n'
        '})();</script>')
    return nodes.raw('', f'<div class="quloud-kept-anchors">{spans}</div>{script}', format='html')


def _english_title(app, docname):
    """The page title without the "(Japanese only)" mark of the navigation."""
    title = app.quloud_english_titles.get(docname) or app.env.titles.get(docname)
    return title.astext() if title is not None else None


def _available(env, published):
    """Docs readable in English: published ones and the indexes leading to them."""
    available = set(published)
    changed = True
    while changed:
        changed = False
        for parent, children in env.toctree_includes.items():
            if parent not in available and available.intersection(children):
                available.add(parent)
                changed = True
    return available


def _japanese_only_mark():
    # A span with a class, so that a style can tell the mark from the title.
    return nodes.inline(' (Japanese only)', ' (Japanese only)', classes=['quloud-japanese-only'])


def mark_untranslated(app, env):
    """Mark the links to untranslated pages, so that readers know before opening them."""
    if app.config.language != 'en':
        return
    available = _available(env, app.quloud_english_published)
    parents = {child: parent for parent, children in env.toctree_includes.items()
               for child in children}
    root = app.config.root_doc
    app.quloud_english_titles = {}
    # The header lists the volumes and has no room for the mark; the landing page
    # marks its links to the untranslated volumes instead (process_doctree).
    app.quloud_untranslated_volumes = {
        doc for doc, parent in parents.items() if parent == root and doc not in available}
    for docname, title in env.titles.items():
        # Mark only the top of an untranslated part (a chapter or an article); its
        # children under the marked link would repeat the same mark.
        parent = parents.get(docname)
        if (docname in available or parent == root
                or (parent in parents and parent not in available
                    and parent not in app.quloud_untranslated_volumes)):
            continue
        app.quloud_english_titles[docname] = title
        marked = title.deepcopy()
        marked += _japanese_only_mark()
        env.titles[docname] = marked
        # The toctrees take the title from the page's own table of contents.
        toc = env.tocs.get(docname)
        link = next((ref for ref in toc.findall(nodes.reference)
                     if not ref.get('anchorname')), None) if toc is not None else None
        if link is not None:
            link += _japanese_only_mark()

    # The standard domain supplies {name} for numbered references to articles.
    # Use the same English title and marker as the toctree for those labels.
    labels = env.domains.standard_domain.labels
    article_ids = {}
    for label, (docname, anchor, _title) in list(labels.items()):
        if docname not in app.quloud_english_titles:
            continue
        if docname not in article_ids:
            article = next(iter(env.get_doctree(docname).findall(nodes.section)), None)
            article_ids[docname] = article['ids'] if article is not None else ()
        if anchor in article_ids[docname]:
            labels[label] = docname, anchor, env.titles[docname].astext()


def check_published(app, env):
    if app.config.language != 'en':
        return
    for docname in sorted(app.quloud_english_published - env.found_docs):
        logger.warning('%s lists %s, which is not a document', PUBLISHED_LIST, docname,
                       type='quloud', subtype='english_edition')


def process_doctree(app, doctree, docname):
    if app.config.language != 'en' or app.builder.format != 'html':
        return
    section = next(iter(doctree.findall(nodes.section)), None)
    if section is None:
        return

    if docname in app.quloud_english_published:
        if docname == app.config.root_doc:
            volumes = {app.builder.get_relative_uri(docname, volume)
                       for volume in app.quloud_untranslated_volumes}
            for ref in doctree.findall(nodes.reference):
                if ref.get('refuri', '').split('#')[0] in volumes:
                    ref += _japanese_only_mark()
            # Orphan pages (old URLs that only redirect to the moved section) are not articles.
            articles = [d for d in app.env.found_docs
                        if d != docname and d not in app.env.toctree_includes
                        and 'orphan' not in app.env.metadata.get(d, {})]
            done = len(app.quloud_english_published.intersection(articles))
            index = section.first_child_not_matching_class(nodes.title)
            if done < len(articles):
                section.insert(len(section) if index is None else index, _notice(
                    f'The English edition is in progress: {done} of {len(articles)} articles '
                    'have been translated so far. Untranslated parts are marked “Japanese only” '
                    'and lead to the Japanese original.', ['quloud-edition-progress']))
        status = _catalog_status(app, docname) or {'fuzzy': 0, 'untranslated': 0}
        status['japanese'] = _japanese_paragraphs(doctree)
        if any(status.values()):
            app.quloud_english_outdated[docname] = status
            logger.warning(
                'English edition is out of date (fuzzy: %d, untranslated: %d, '
                'paragraphs in Japanese: %d); run "make update-po" and translate them',
                status['fuzzy'], status['untranslated'], status['japanese'],
                location=docname, type='quloud', subtype='english_outdated')
            notice = _notice(
                'This translation may be out of date: the Japanese original has been '
                'revised since it was translated.', ['quloud-edition-outdated'],
                'Read the Japanese original', _japanese_url(docname))
            index = section.first_child_not_matching_class(nodes.title)
            section.insert(len(section) if index is None else index, notice)
        return

    # Keep the page and its section ids (for the numbering and the incoming links),
    # but show only the English title, a link to the original, and the toctrees.
    title = section.next_node(nodes.title)
    english = _english_title(app, docname)
    if english and title is not None:
        title[:] = [nodes.Text(english)]
    toctrees = [node for node in section.findall(nodes.compound)
                if 'toctree-wrapper' in node.get('classes', [])]
    # Translated pages link to sections, equations and figures of this page; keep
    # their ids, so that such a link lands on the notice instead of failing.
    kept = [i for node in section.findall(nodes.Element) if node is not section
            for i in node.get('ids', [])]
    section[:] = [title] if title is not None else []
    section += _notice(
        'This page has not been translated into English yet.',
        ['quloud-edition-untranslated'],
        'Read the Japanese original', _japanese_url(docname),
        'In desktop Chrome, the language menu on that page can show a machine translation.')
    if kept:
        section += _kept_anchors(kept)
    section.extend(toctrees)
    for node in list(doctree.children):
        if node is not section and not isinstance(node, nodes.target):
            doctree.remove(node)


def add_page_context(app, pagename, _templatename, context, doctree):
    english = app.config.language == 'en'
    published = pagename in app.quloud_english_published
    if english:
        context['quloud_japanese_url'] = _japanese_url(pagename)
    elif published:
        context['quloud_english_url'] = _english_url(pagename)

    if english and doctree is not None and not published:
        # The page body was replaced; drop the Japanese headings and title.
        context.pop('toc', None)
        title = _english_title(app, pagename)
        if title:
            context['title'] = title

    if published:
        ja = app.config.quloud_japanese_baseurl + pagename + '.html'
        en = app.config.quloud_english_baseurl + pagename + '.html'
        context['metatags'] = context.get('metatags', '') + (
            f'\n<link rel="alternate" hreflang="ja" href="{ja}" />'
            f'\n<link rel="alternate" hreflang="en" href="{en}" />'
            f'\n<link rel="alternate" hreflang="x-default" href="{ja}" />')


def write_status(app, exception):
    if exception or app.config.language != 'en' or app.builder.format != 'html':
        return
    status = {
        'published': sorted(app.quloud_english_published),
        'outdated': dict(sorted(app.quloud_english_outdated.items())),
    }
    path = Path(app.outdir) / 'published.json'
    path.write_text(json.dumps(status, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def builder_inited(app):
    app.quloud_english_published = read_published(app.confdir)
    app.quloud_english_outdated = {}
    app.quloud_english_titles = {}
    app.quloud_untranslated_volumes = set()


def setup(app):
    app.add_directive('translatable-raw', TranslatableRaw)
    app.add_config_value('quloud_japanese_baseurl', '', 'html')
    app.add_config_value('quloud_english_baseurl', '', 'html')
    app.connect('builder-inited', builder_inited)
    app.connect('env-check-consistency', check_published)
    # After conf.py's localize_navigation has put the English labels into env.titles.
    app.connect('env-updated', mark_untranslated, priority=600)
    app.connect('doctree-resolved', process_doctree)
    app.connect('html-page-context', add_page_context)
    app.connect('build-finished', write_status)
    return {'parallel_read_safe': True, 'parallel_write_safe': False}
