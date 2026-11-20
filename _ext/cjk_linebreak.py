"""Remove line breaks between Japanese characters in the rendered text.

reStructuredText keeps a line break inside a paragraph as a newline, and the
browser shows it as a space. Japanese text has no spaces between words, so a
source line wrapped in the middle of a sentence shows a stray space. This
post-transform drops a newline when the characters on both sides are CJK
characters, also across inline markup such as **strong** or :ref:. Literal
text, math and raw nodes are left untouched. Lines ending with a backslash
already have no newline and are not affected.
"""
import re

from docutils import nodes
from sphinx.transforms.post_transforms import SphinxPostTransform

CJK = "　-ヿ㐀-䶿一-鿿豈-﫿＀-￯"
IS_CJK = re.compile(f"[{CJK}]")
INNER = re.compile(f"(?<=[{CJK}])\n(?=[{CJK}])")
PROTECTED = (nodes.FixedTextElement, nodes.literal, nodes.math, nodes.math_block, nodes.raw,
             nodes.comment)


def _protected(node):
    while node is not None:
        if isinstance(node, PROTECTED):
            return True
        node = node.parent
    return False


class RemoveCJKLineBreaks(SphinxPostTransform):
    default_priority = 900

    def run(self, **kwargs):
        for block in list(self.document.findall(nodes.TextElement)):
            if isinstance(block.parent, nodes.TextElement) or _protected(block):
                continue
            texts = list(block.findall(nodes.Text))
            for i, text in enumerate(texts):
                if _protected(text.parent):
                    continue
                s = str(text)
                new = INNER.sub("", s)
                prev = str(texts[i - 1])[-1:] if i > 0 else ""
                nxt = str(texts[i + 1])[:1] if i + 1 < len(texts) else ""
                if new.startswith("\n") and IS_CJK.match(prev) and IS_CJK.match(new[1:2]):
                    new = new[1:]
                if new.endswith("\n") and IS_CJK.match(new[-2:-1]) and IS_CJK.match(nxt):
                    new = new[:-1]
                if new != s:
                    text.parent.replace(text, nodes.Text(new))


def setup(app):
    app.add_post_transform(RemoveCJKLineBreaks)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
