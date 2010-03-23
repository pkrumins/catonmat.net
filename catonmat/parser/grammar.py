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
    DocumentNode, ParagraphNode, TextNode, CommentNode, InlineTagNode,
    SelfClosingTagNode, BlockTagNode, LiteralNode,
    accept_token, extract_tag_name, skip_token,
    DONT_P
)

from pygments.token         import Token

# ----------------------------------------------------------------------------

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

