#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from catonmat.parser.util   import *

from pygments.lexer         import RegexLexer
from pygments.token         import Token
from pygments               import format, lex

from StringIO               import StringIO

import re

class PageLexer(RegexLexer):
    def open_tag(lexer, match):
        tag_name = match.group(1).lower()
        if tag_name in SELF_CLOSING_TAGS:
            tag_type = Token.Tag.SelfClosingTag
        elif tag_name in INLINE_TAGS:
            tag_type = Token.Tag.InlineTag
        else:
            tag_type = Token.Tag.BlockTag
        yield match.start(), tag_type, match.group(0).lower()

    flags = re.IGNORECASE | re.DOTALL
    tokens = {
        'root': [
            (r'\n\n+',               Token.Par),
            (r'\n',                  Token.Br),
            (r'[^<\n]+',             Token.Text),
            (r'<!--.*?-->',          Token.Comment),
            (r'<pre>(.+?)</pre>',    Token.Text.Pre),
            (r'<([a-zA-Z0-9]+).*?>', open_tag),
            (r'</[^>]+>',            Token.Tag.Close)
        ],
    }

def gdocument(token_stream):
    root = DocumentNode()
    while True:
        if accept(token_stream, Token.Par):
            skip_token(token_stream)
        elif accept(token_stream, Token.Br):
            skip_token(token_stream)
        elif accept(token_stream, Token.Comment):
            skip_token(token_stream)
            root.append(CommentNode(token_stream.value))
        elif accept(token_stream, Token.Text):
            p = gparagraph(token_stream)
            root.append(p)
        elif accept(token_stream, Token.Tag.SelfClosingTag):
            p = gparagraph(token_stream)
            root.append(p)
        elif accept(token_stream, Token.Tag.InlineTag):
            p = gparagraph(token_stream)
            root.append(p)
        elif accept(token_stream, Token.Tag.BlockTag):
            block = gblock(token_stream)
            root.append(block)
        else:
            return root

def gparagraph(token_stream):
    p = ParagraphNode()
    while True:
        if accept(token_stream, Token.Par):
            skip_token(token_stream)
            return p
        elif accept(token_stream, Token.Br):
            p.append(gbr(token_stream))
        elif accept(token_stream, Token.Comment):
            p.append(CommentNode(token_stream.value))
        elif accept(token_stream, Token.Text):
            p.append(TextNode(token_stream.value))
        elif accept(token_stream, Token.Tag.SelfClosingTag):
            p.append(SelfClosingTagNode(token_stream.value))
        elif accept(token_stream, Token.Tag.InlineTag):
            inline_tag = ginline_tag(token_stream)
            p.append(inline_tag)
        elif accept(token_stream, Token.Tag.BlockTag):
            return p
        else:
            return p

def gbr(token_stream):
    skip_token(token_stream)
    br = SelfClosingTagNode("<br>")
    if not accept(token_stream, Token.Tag.Close):
        return br
    return None

def ginline_tag(token_stream):
    inline_tag = InlineTagNode(token_stream.value)
    while True:
        if accept(token_stream, Token.Tag.Close): # assume correctly nested and closed tags
            skip_token(token_stream)
            return inline_tag
        elif accept(token_stream, Token.Par):
            skip_token(token_stream)
        elif accept(token_stream, Token.Br):
            inline_tag.append(gbr(token_stream))
        elif accept(token_stream, Token.Comment):
            inline_tag.append(CommentNode(token_stream.value))
        elif accept(token_stream, Token.Text):
            inline_tag.append(TextNode(token_stream.value))
        elif accept(token_stream, Token.Tag.SelfClosingTag):
            inline_tag.append(SelfClosingTagNode(token_stream.value))
        elif accept(token_stream, Token.Tag.InlineTag):
            nested_inline_tag = ginline_tag(token_stream)
            inline_tag.append(nested_inline_tag)
        elif accept(token_stream, Token.Tag.BlockTag):
            return inline_tag
        else:
            return inline_tag
        
def gblock(token_stream):
    block = BlockTagNode(token_stream.value)
    while True:
        if accept(token_stream, Token.Tag.Close): #assume correctly nested and closed tags
            skip_token(token_stream)
            return block
        elif accept(token_stream, Token.Par):
            skip_token(token_stream)
        elif accept(token_stream, Token.Br):
            skip_token(token_stream)
        elif accept(token_stream, Token.Comment):
            block.append(CommentNode(token_stream.value))
        elif accept(token_stream, Token.Text):
            p = gparagraph(token_stream)
            block.append(p)
        elif accept(token_stream, Token.Tag.SelfClosingTag):
            p = gparagraph(token_stream)
            block.append(p)
        elif accept(token_stream, Token.Tag.InlineTag):
            p = gparagraph(token_stream)
            block.append(p)
        elif accept(token_stream, Token.Tag.BlockTag):
            nested_block = gblock(token_stream)
            block.append(nested_block)
        else:
            return block

def build_parse_tree(token_stream):
    return gdocument(token_stream)

def empty_text(text):
    return text.isspace()

def empty_pred(node):
    if isinstance(node, TextNode):
        return empty_text(node.value)
    elif isinstance(node, SelfClosingTagNode):
        return extract_tag_name(node.value) == 'br'
    return False

def empty_paragraph(p):
    """ A paragraph is empty if it contains only empty text nodes and <br>s """
    return all(empty_pred(pnode) for pnode in p)

def empty_node(node):
    if isinstance(node, ParagraphNode):
        return empty_paragraph(node)
    return False

def filter_tree(tree):
    tree.children = [filter_tree(child_node) for child_node in \
            tree.children if not empty_node(child_node)]
    return tree

def build_html(tree, out_file):
    for node in tree:
        if isinstance(node, ParagraphNode):
            out_file.write("<p>")
        elif isinstance(node, TextNode):
            out_file.write(node.value)
        elif isinstance(node, CommentNode):
            out_file.write(node.value)
        elif isinstance(node, InlineTagNode):
            out_file.write(node.value)
        elif isinstance(node, BlockTagNode):
            out_file.write(node.value)
            out_file.write("\n")
        elif isinstance(node, SelfClosingTagNode):
            tag = extract_tag_name(node.value)
            if tag == 'br':
                out_file.write("<br>\n")
            else:
                out_file.write(node.value)

        build_html(node, out_file)

        if isinstance(node, ParagraphNode):
            out_file.write("</p>\n")
        elif isinstance(node, InlineTagNode):
            tag = extract_tag_name(node.value)
            out_file.write("</%s>" % tag)
        elif isinstance(node, BlockTagNode):
            tag = extract_tag_name(node.value)
            out_file.write("</%s>\n" % tag)

def page_lexer(text):
    return TokenGenerator(GeneratorWithoutLast(lex(text, PageLexer())))

def parse_page(text):
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    token_stream = page_lexer(text)

    # first stage tree contains the full parse tree, including empty nodes
    # such as <p>       </p> and <p>   <br>   </p>.
    first_stage_tree = build_parse_tree(token_stream)

    # second stage tree clears up the empty text elements
    second_stage_tree = filter_tree(first_stage_tree)

    buffer = StringIO()
    build_html(second_stage_tree, buffer)
    return buffer.getvalue()

