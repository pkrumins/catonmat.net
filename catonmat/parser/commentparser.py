#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from catonmat.parser.util   import (
    get_lexer, extract_tag_name, document_lexer,
    DocumentNode, ParagraphNode, TextNode, CommentNode, InlineTagNode,
    SelfClosingTagNode, BlockTagNode, LiteralNode,
)

from catonmat.parser.grammar import gdocument
from catonmat.parser.filter  import filter_tree

from StringIO               import StringIO
from urlparse               import urlparse

import re

# ----------------------------------------------------------------------------

ALLOWED_COMMENT_TAGS = [
    'a', 'b', 'strong', 'i', 'em', 'q', 'blockquote', 'code', 'pre', 'sub',
    'sup',
    'div', 'span'
]
ALLOWED_COMMENT_URL_SCHEMES = [ 'http', 'https', 'ftp' ]

href_re = re.compile(r"""href="([^"]+)"|href='([^']+)'""")
class_re = re.compile(r'class="([^"]+)"')

def build_parse_tree(token_stream):
    return gdocument(token_stream)

def allowed_tag(tag):
    return tag in ALLOWED_COMMENT_TAGS

def normalize_href(href):
    url = urlparse(href)
    check_scheme = True
    if not url.scheme:
        href = 'http://' + href
        check_scheme = False
    if check_scheme:
        if url.scheme not in ALLOWED_COMMENT_URL_SCHEMES:
            return None
    return href

def handle_a_tag(node, writable):
    match = href_re.search(node.value)
    if match:
        href = match.group(1) or match.group(2)
        href = normalize_href(href)
        if href:
            writable.write("""<a href="%s">""" % href)
            return
    writable.write("<a>")

def should_traverse_children(tag):
    return allowed_tag(tag)

def extract_class(tag):
    match = class_re.search(tag)
    if match:
        return match.group(1)
    return None

def handle_tag(node, tag, writable):
    if tag == 'a':
        handle_a_tag(node, writable)
    elif tag == 'div':
        if extract_class(node.value) == 'highlight':
            writable.write('<div class="highlight">')
        else:
            writable.write('<div>')
    elif tag == 'span':
        klass = extract_class(node.value)
        if klass:
            writable.write('<span class="%s">' % klass)
        else:
            writable.write('<span>')
    else:
        writable.write("<%s>" % tag)

def handle_disallowed_tag(node, tag, writable):
    writable.write("&lt;%s&gt;" % tag)
    build_html(node, writable)

def handle_tag_node(node, tag, writable):
    if allowed_tag(tag):
        handle_tag(node, tag, writable)
    else:
        handle_disallowed_tag(node, tag, writable)

def build_html(parse_tree, writable):
    for node in parse_tree:
        traverse_children = True
        if isinstance(node, ParagraphNode):
            writable.write("<p>")
        elif isinstance(node, TextNode):
            writable.write(node.value)
        elif isinstance(node, InlineTagNode) or \
                isinstance(node, BlockTagNode):
            tag = extract_tag_name(node.value)
            handle_tag_node(node, tag, writable)
            traverse_children = should_traverse_children(tag)
        elif isinstance(node, SelfClosingTagNode):
            tag = extract_tag_name(node.value)
            if tag == 'br':
                writable.write("<br>\n")

        if traverse_children:
            build_html(node, writable)

            if isinstance(node, ParagraphNode):
                writable.write("</p>\n")
            elif isinstance(node, InlineTagNode):
                tag = extract_tag_name(node.value)
                writable.write("</%s>" % tag)
            elif isinstance(node, BlockTagNode):
                tag = extract_tag_name(node.value)
                writable.write("</%s>\n" % tag)

def parse_comment(text):
    from catonmat.parser.lexer   import CommentLexer
    # TODO: this method is 1:1 as pageparser.py:parsepage(),
    #       merge them!
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    token_stream = get_lexer(text, CommentLexer)

    # first stage tree contains the full parse tree, including empty nodes
    # such as <p>       </p> and <p>   <br>   </p>.
    first_stage_tree = build_parse_tree(token_stream)

    # second stage tree clears up the empty text elements
    second_stage_tree = filter_tree(first_stage_tree)

    buffer = StringIO()
    build_html(second_stage_tree, buffer)
    return buffer.getvalue()

