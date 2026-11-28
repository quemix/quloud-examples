"""Point links to the partner site (technical notes / calculation examples) at its English edition.

In the English build, a link such as ``https://technical-notes.quemix.com/solid/phonon.html#x``
becomes ``https://technical-notes.quemix.com/en/solid/phonon.html#x`` when the partner site lists
``solid/phonon`` in its ``en/published.json`` (written by ``_ext/english_edition.py``). Links to
pages that are not published in English keep pointing at the Japanese original.

``quloud_partner_sites`` in ``conf.py`` maps the partner's base URL to the URL of that list.
The environment variable ``QULOUD_PARTNER_PUBLISHED`` may name a local copy of the list instead
(for builds without network access, e.g. the partner's ``_build/html/en/published.json``).
If the list cannot be read, the build warns and keeps all links pointing at Japanese pages.
"""

import json
import os
import urllib.request

from docutils import nodes
from sphinx.util import logging

logger = logging.getLogger(__name__)


def _read_published(source):
    if source.startswith(('http://', 'https://')):
        with urllib.request.urlopen(source, timeout=20) as response:
            data = json.load(response)
    else:
        with open(source, encoding='utf-8') as f:
            data = json.load(f)
    return set(data['published'])


def builder_inited(app):
    app.quloud_partner_published = {}
    if app.config.language != 'en':
        return
    override = os.environ.get('QULOUD_PARTNER_PUBLISHED')
    for base, source in app.config.quloud_partner_sites.items():
        source = override or source
        try:
            app.quloud_partner_published[base] = _read_published(source)
        except (OSError, ValueError, KeyError) as error:
            logger.warning('cannot read the English pages of %s from %s (%s); links to it '
                           'stay on the Japanese pages', base, source, error,
                           type='quloud', subtype='partner_links')


def _english_uri(base, published, refuri):
    path, hash_, fragment = refuri[len(base):].partition('#')
    if path.startswith('en/'):
        return None
    docname = 'index' if path in ('', 'index.html') else path.removesuffix('.html')
    if docname not in published:
        return None
    return base + 'en/' + path + hash_ + fragment


def process_doctree(app, doctree, _docname):
    if app.config.language != 'en':
        return
    for base, published in app.quloud_partner_published.items():
        for ref in doctree.findall(nodes.reference):
            refuri = ref.get('refuri', '')
            if refuri.startswith(base):
                english = _english_uri(base, published, refuri)
                if english:
                    ref['refuri'] = english


def add_page_context(app, _pagename, _templatename, context, _doctree):
    """Give templates the partner's top page in the reader's language."""
    for base, published in app.quloud_partner_published.items():
        context['quloud_partner_url'] = base + 'en/' if 'index' in published else base
        break


def setup(app):
    app.add_config_value('quloud_partner_sites', {}, 'html')
    app.connect('builder-inited', builder_inited)
    app.connect('doctree-resolved', process_doctree)
    app.connect('html-page-context', add_page_context)
    return {'parallel_read_safe': True, 'parallel_write_safe': True}
