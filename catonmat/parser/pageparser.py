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
    tag_type_by_name, get_lexer, extract_tag_name, accept_token, skip_token,
    DocumentNode, ParagraphNode, TextNode, CommentNode, InlineTagNode,
    SelfClosingTagNode, BlockTagNode, LiteralNode,
    DONT_P
)

from pygments               import highlight
from pygments.token         import Token
from pygments.lexer         import RegexLexer, bygroups, using
from pygments.lexers        import get_lexer_by_name
from pygments.formatters    import HtmlFormatter

from StringIO               import StringIO

import re

# ----------------------------------------------------------------------------

class PageLexer(RegexLexer):
    def open_tag_handler(lexer, match):
        tag_name = match.group(1).lower()
        tag_type = tag_type_by_name(tag_name)
        yield match.start(), tag_type, match.group(0).lower()

    def pure_pre_handler(lexer, match):
        yield_items = [
            (Token.Tag.BlockTag, "<pre>"),
            (Token.Text, match.group(1)),
            (Token.Tag.Close, "</pre>")
        ]
        for token, value in yield_items:
            yield match.start(), token, value

    def lang_pre_handler(lexer, match):
        lang = match.group(1)
        code = match.group(2)
        lang_lexer = get_lexer_by_name(lang, stripall=True)
        token_stream = page_lexer(highlight(code, lang_lexer, HtmlFormatter()))
        for token, value in token_stream:
            yield match.start(), token, value

    flags = re.IGNORECASE | re.DOTALL
    tokens = {
        'root': [
            (r'\n\n+',               Token.Par),
            (r'\n',                  Token.Br),
            (r'[^<\n]+',             Token.Text),
            (r'<!--.*?-->',          Token.Comment),
            (r'<pre>(.+?)</pre>',    pure_pre_handler),
            (r'<pre lang="(.+?)">(.+?)</pre>',    lang_pre_handler),
            (r'<([a-zA-Z0-9]+).*?>', open_tag_handler),
            (r'</[^>]+>',            Token.Tag.Close)
        ],
    }

def gdocument(token_stream):
    root = DocumentNode()
    while True:
        if accept_token(token_stream, Token.Par):
            skip_token(token_stream)
        elif accept_token(token_stream, Token.Br):
            skip_token(token_stream)
        elif accept_token(token_stream, Token.Literal):
            root.append(LiteralNode(token_stream.value))
        elif accept_token(token_stream, Token.Comment):
            root.append(CommentNode(token_stream.value))
        elif accept_token(token_stream, Token.Text):
            p = gparagraph(token_stream)
            root.append(p)
        elif accept_token(token_stream, Token.Tag.SelfClosingTag):
            p = gparagraph(token_stream)
            root.append(p)
        elif accept_token(token_stream, Token.Tag.InlineTag):
            p = gparagraph(token_stream)
            root.append(p)
        elif accept_token(token_stream, Token.Tag.BlockTag):
            block = gblock(token_stream)
            root.append(block)
        else:
            return root

def gparagraph(token_stream):
    p = ParagraphNode()
    while True:
        if accept_token(token_stream, Token.Par):
            skip_token(token_stream)
            return p
        elif accept_token(token_stream, Token.Br):
            p.append(gbr(token_stream))
        elif accept_token(token_stream, Token.Literal):
            p.append(LiteralNode(token_stream.value))
        elif accept_token(token_stream, Token.Comment):
            p.append(CommentNode(token_stream.value))
        elif accept_token(token_stream, Token.Text):
            p.append(TextNode(token_stream.value))
        elif accept_token(token_stream, Token.Tag.SelfClosingTag):
            p.append(SelfClosingTagNode(token_stream.value))
        elif accept_token(token_stream, Token.Tag.InlineTag):
            inline_tag = ginline_tag(token_stream)
            p.append(inline_tag)
        elif accept_token(token_stream, Token.Tag.BlockTag):
            return p
        else:
            return p

def gbr(token_stream):
    skip_token(token_stream)
    br = SelfClosingTagNode("<br>")
    if accept_token(token_stream, Token.Tag.BlockTag):
        return None
    if accept_token(token_stream, Token.Tag.Close):
        return None
    return br

def ginline_tag(token_stream):
    inline_tag = InlineTagNode(token_stream.value)
    while True:
        if accept_token(token_stream, Token.Tag.Close): # assume correctly nested and closed tags
            skip_token(token_stream)
            return inline_tag
        elif accept_token(token_stream, Token.Par):
            skip_token(token_stream)
        elif accept_token(token_stream, Token.Br):
            inline_tag.append(gbr(token_stream))
        elif accept_token(token_stream, Token.Literal):
            inline_tag.append(LiteralNode(token_stream.value))
        elif accept_token(token_stream, Token.Comment):
            inline_tag.append(CommentNode(token_stream.value))
        elif accept_token(token_stream, Token.Text):
            inline_tag.append(TextNode(token_stream.value))
        elif accept_token(token_stream, Token.Tag.SelfClosingTag):
            inline_tag.append(SelfClosingTagNode(token_stream.value))
        elif accept_token(token_stream, Token.Tag.InlineTag):
            nested_inline_tag = ginline_tag(token_stream)
            inline_tag.append(nested_inline_tag)
        elif accept_token(token_stream, Token.Tag.BlockTag):
            return inline_tag
        else:
            return inline_tag

def block_try_p(tag_name, token_stream, node_type, nonterminal=None):
    if tag_name in DONT_P:
        if nonterminal:
            return nonterminal(token_stream)
        return node_type(token_stream.value)
    else:
        return gparagraph(token_stream)

def gblock(token_stream):
    block = BlockTagNode(token_stream.value)
    tag_name = extract_tag_name(block.value)
    while True:
        if accept_token(token_stream, Token.Tag.Close): #assume correctly nested and closed tags
            skip_token(token_stream)
            return block
        elif accept_token(token_stream, Token.Par):
            skip_token(token_stream)
        elif accept_token(token_stream, Token.Br):
            skip_token(token_stream)
        elif accept_token(token_stream, Token.Literal):
            block.append(LiteralNode(token_stream.value))
        elif accept_token(token_stream, Token.Comment):
            block.append(CommentNode(token_stream.value))
        elif accept_token(token_stream, Token.Text):
            block.append(block_try_p(tag_name, token_stream, TextNode))
        elif accept_token(token_stream, Token.Tag.SelfClosingTag):
            block.append(block_try_p(tag_name, token_stream, SelfClosingTagNode))
        elif accept_token(token_stream, Token.Tag.InlineTag):
            block.append(block_try_p(tag_name, token_stream, InlineTagNode, ginline_tag))
        elif accept_token(token_stream, Token.Tag.BlockTag):
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
        elif isinstance(node, LiteralNode):
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
            out_file.write("\n</%s>\n" % tag)

def page_lexer(text):
    return get_lexer(text, PageLexer)

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

