#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from pygments.lexer         import RegexLexer
from pygments.token         import Token
from pygments               import format, lex

from StringIO               import StringIO

import re

SELF_CLOSING_TAGS = frozenset(['img', 'br', 'hr', 'input'])
INLINE_TAGS = frozenset([
    'a',      'abbr', 'acronym', 'b',        'bdo',   'big',  'cite',
    'code',   'dfn',  'em',      'font',     'i',     'kbd',  'label',
    'q',      's',    'samp',    'select',   'small', 'span', 'strike',
    'strong', 'sub',  'sup',     'textarea', 'tt',    'u',    'var'
])

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

class TokenGenerator(object):
    """
    Given a generator from Pygments, this wrapper adds peek() method to look
    into the future, and adds several other convenience properties.
    """
    NONE = object()

    def __init__(self, generator):
        self.generator = generator
        self.peeked_value = self.NONE

    def peek(self):
        """ Peek for the next value in the generator """
        if self.peeked_value is self.NONE:
            # May throw StopIteration if we try to peek beyond last element
            self.peeked_value = self.generator.next()
            return self.peeked_value
        return self.peeked_value

    def _xyzzy(self, method, index):
        try:
            return method()[index]
        except StopIteration:
            return None

    @property
    def token(self):
        """ Get just the token in the generator """
        return self._xyzzy(self.next, 0)

    @property
    def value(self):
        """ Get just the value in the generator """
        return self._xyzzy(self.next, 1)

    @property
    def peek_token(self):
        """ Peek just the token in the generator """
        return self._xyzzy(self.peek, 0)

    @property
    def peek_value(self):
        """ Peek just the value in the generator """
        return self._xyzzy(self.peek, 1)

    def __iter__(self):
        while True:
            yield self.next()

    def next(self):
        if self.peeked_value is not self.NONE:
            peeked_value, self.peeked_value = self.peeked_value, self.NONE
            return peeked_value
        else:
            return self.generator.next()

def GeneratorWithoutLast(generator):
    """
    Pygments has a nasty property that it adds a new-line at the end of the
    parsed token list. This generator wrapper drops the last token in the stream.
    """
    last = generator.next()
    for val in generator:
        yield last
        last = val

class Node(object):
    def __init__(self, value=None):
        self.value = value
        self.parent = None
        self.children = []

    def append(self, node):
        if node:
            node.parent = self
            self.children.append(node)

    def __iter__(self):
        for child in self.children:
            yield child

    def __repr__(self):
        return "<Node(%s)>" % self.__class__.__name__

class DocumentNode(Node):
    pass

class ParagraphNode(Node):
    pass

class TextNode(Node):
    pass

class CommentNode(Node):
    pass

class InlineTagNode(Node):
    pass

class SelfClosingTagNode(Node):
    pass

class BlockTagNode(Node):
    pass

def accept(token_stream, token):
    return token_stream.peek_token == token

def skip_token(token_stream):
    token_stream.next()

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

def walk(root, indent):
    for node in root.children:
        if indent:
            print " "*(4*indent), node, node.value
        else:
            print node, node.value
        walk(node, indent+1)

def extract_tag_name(value):
    matches = re.match(r'<([a-zA-Z0-9]+)', value)
    if matches:
        return matches.group(1)
    raise ValueError("Tag '%s' didn't match regex" % value)

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

