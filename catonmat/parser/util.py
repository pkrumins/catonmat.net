#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from pygments           import lex
from pygments.token     import Token

import re

# ----------------------------------------------------------------------------

SELF_CLOSING_TAGS = frozenset(['img', 'br', 'hr', 'input'])
INLINE_TAGS = frozenset([
    'a',      'abbr', 'acronym', 'b',        'bdo',   'big',  'cite',
    'code',   'dfn',  'em',      'font',     'i',     'kbd',  'label',
    'q',      's',    'samp',    'select',   'small', 'span', 'strike',
    'strong', 'sub',  'sup',     'textarea', 'tt',    'u',    'var'
])

def tag_type_by_name(tag_name):
    if tag_name in SELF_CLOSING_TAGS:
        return Token.Tag.SelfClosingTag
    elif tag_name in INLINE_TAGS:
        return Token.Tag.InlineTag
    else:
        return Token.Tag.BlockTag

def extract_tag_name(value):
    matches = re.match(r'<([a-zA-Z0-9]+)', value)
    if matches:
        return matches.group(1)
    raise ValueError("Tag '%s' didn't match regex" % value)

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

def get_lexer(text, lexer):
    return TokenGenerator(GeneratorWithoutLast(lex(text, lexer())))

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

class LiteralNode(Node):
    pass

class CommentNode(Node):
    pass

class InlineTagNode(Node):
    pass

class SelfClosingTagNode(Node):
    pass

class BlockTagNode(Node):
    pass

def accept_token(token_stream, token):
    return token_stream.peek_token == token

def skip_token(token_stream):
    token_stream.next()

def walk(root, indent=0):
    for node in root:
        if indent:
            print " "*(4*indent), node, node.value
        else:
            print node, node.value
        walk(node, indent+1)

