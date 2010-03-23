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

from catonmat.parser.lexer   import DocumentLexer
from catonmat.parser.grammar import gdocument
from catonmat.parser.filter  import filter_tree

from StringIO               import StringIO

# ----------------------------------------------------------------------------

def build_parse_tree(token_stream):
    return gdocument(token_stream)

def build_html(tree, writable):
    for node in tree:
        if isinstance(node, ParagraphNode):
            writable.write("<p>")
        elif isinstance(node, TextNode):
            writable.write(node.value)
        elif isinstance(node, LiteralNode):
            writable.write(node.value)
        elif isinstance(node, CommentNode):
            writable.write(node.value)
        elif isinstance(node, InlineTagNode):
            writable.write(node.value)
        elif isinstance(node, BlockTagNode):
            writable.write(node.value)
            writable.write("\n")
        elif isinstance(node, SelfClosingTagNode):
            tag = extract_tag_name(node.value)
            if tag == 'br':
                writable.write("<br>\n")
            else:
                writable.write(node.value)

        build_html(node, writable)

        if isinstance(node, ParagraphNode):
            writable.write("</p>\n")
        elif isinstance(node, InlineTagNode):
            tag = extract_tag_name(node.value)
            writable.write("</%s>" % tag)
        elif isinstance(node, BlockTagNode):
            tag = extract_tag_name(node.value)
            writable.write("\n</%s>\n" % tag)

def parse_page(text):
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    token_stream = get_lexer(text, DocumentLexer)

    # first stage tree contains the full parse tree, including empty nodes
    # such as <p>       </p> and <p>   <br>   </p>.
    first_stage_tree = build_parse_tree(token_stream)

    # second stage tree clears up the empty text elements
    second_stage_tree = filter_tree(first_stage_tree)

    buffer = StringIO()
    build_html(second_stage_tree, buffer)
    return buffer.getvalue()

