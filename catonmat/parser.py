#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website. See this post for more info:
# http://www.catonmat.net/blog/50-ideas-for-the-new-catonmat-website/
#
# Code is licensed under GNU GPL license.
#

from pygments.lexer         import RegexLexer
from pygments.token         import Token, Text, Comment, Error, Whitespace
from pygments               import format, lex

from StringIO               import StringIO

import re

# ----------------------------------------------------------------------------

Tag = Token.Tag

class PageLexer(RegexLexer):
    flags = re.IGNORECASE | re.DOTALL
    tokens = {
        'root': [
            (r'\n\n',               Text.Par),
            (r'\n',                 Text.Br),
            (r'[^<\n]+',            Text),
            (r'<!--',               Comment,    'comment'),
            (r'<\s*[a-zA-Z0-9:]+',  Tag.Open,   'tag'),
            (r'<\s*/\s*[^>]+>',     Tag.Close),
        ],
        'comment': [
            (r'[^-]+', Comment),
            (r'-->',   Comment,  '#pop'),
            (r'-',     Comment),
        ],
        'tag': [
            (r'[^>]+', Tag.Contents),
            (r'>',     Tag.End,  '#pop'),
        ],
    }


class CommentLexer(RegexLexer):
    flags = re.IGNORECASE | re.DOTALL
    tokens = {
        'a': [
            (r'\s*',          Whitespace),
            (r'href="[^"]+"', Tag.Attribute), # TODO: xss
            (r"href='[^']+'", Tag.Attribute),
            (r'>',            Tag.Close, '#pop')
        ],
        'code': [
            (r'\s*',          Whitespace),
            (r'lang="[^"]+"', Tag.Code.Lang),
            (r"lang='[^']+'", Tag.Code.Lang),
            (r'>',            Tag.Close, '#pop')
        ],
        'root': [
            (r'\n\n',       Text.Par),
            (r'[^<\n]+',    Text),
            (r'<(b|i|q)>',  Tag.Allowed),
            (r'<a',         Tag.Allowed, 'a'),
            (r'<code',      Tag.Allowed, 'code'),
            (r'<',          Tag.Open)
        ]
    }


class GeneratorWithPeek(object):
    """ Given a generator, makes it peek()-able """
    def __init__(self, generator):
        self.generator = generator
        self.peeked_value = None

    def peek(self):
        """ Peek for the next value in generator """
        if self.peeked_value is None:
            # May throw StopIteration if we try to peek beyond last element
            self.peeked_value = self.generator.next()
            return self.peeked_value
        return self.peeked_value

    def __iter__(self):
        while True:
            yield self.next()

    def next(self):
        if self.peeked_value:
            peeked_value = self.peeked_value
            self.peeked_value = None
            return peeked_value
        else:
            return self.generator.next()


class HtmlState(object):
    self_closing_tags = frozenset(['img', 'br', 'hr', 'input'])
    inline_tags = frozenset(['a',      'abbr', 'acronym', 'b',        'bdo',   'big',  'cite',
                             'code',   'dfn',  'em',      'font',     'i',     'kbd',  'label',
                             'q',      's',    'samp',    'select',   'small', 'span', 'strike',
                             'strong', 'sub',  'sup',     'textarea', 'tt',    'u',    'var'])
    dont_p = frozenset(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'li'])

    def __init__(self):
        self.par_started = False
        self.in_tags = []

    def should_p(self):
        a = self.in_tag() not in HtmlState.inline_tags
        b = self.in_tag() not in HtmlState.dont_p
        return a and b

    def in_tag(self):
        if self.in_tags:
            return self.in_tags[-1]
        return None

    def enter_tag(self, tag):
        if tag not in HtmlState.self_closing_tags:
            self.in_tags.append(tag)

    def leave_tag(self):
        try:
            self.in_tags.pop()
        except IndexError:
            pass


def extract_tag_name(value):
    matches = re.match(r'<\s*([a-zA-Z0-9:]+)', value)
    if matches:
        return matches.group(1)
    raise ValueError("Tag '%s' didn't match regex" % value)


def page_token_processor(html_state, token, value, prev_token, next_token):
    """ Process a (token, value) based on prev_token, next_token and current html_state """
    if token is Text:
        if not html_state.par_started:
            if html_state.should_p():
                html_state.par_started = True
                return "<p>" + value
        return value

    if token is Tag.Open:
        tag = extract_tag_name(value)
        html_state.enter_tag(tag)
        return value

    if token is Tag.Close:
        html_state.leave_tag()

    if token is Text.Par:
        html_state.par_started = False

    if token is Text.Br:
        if prev_token is Tag.Text:
            return "<br>"

    if token is Error:
        return "<span style=\"color: red; font-size: 2em\">Error: " + value + "</span>"

    return value


def comment_token_processor(html_state, token, value, prev_token, next_token):
    if token is Tag.Open:
        return "&lt;"

    if token is Text.Par:
        return "\n<p>"

    return value


def build_html(tokenstream, token_processor):
    outfile = StringIO()
    html_state = HtmlState()
    prev_token = None

    for token, value in tokenstream:
        try:
            next_token, _ = tokenstream.peek()
        except StopIteration:
            next_token = None

        outfile.write(token_processor(html_state, token, value, prev_token, next_token))
        prev_token = token

    return outfile.getvalue()

def parse(text, lexer, processor):
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = re.sub(r'\n\n+', '\n\n', text)

    print text
    return text

    tokenstream = GeneratorWithPeek(lex(text, lexer()))
    return build_html(tokenstream, processor)


def parse_page(page):
    return parse(page, PageLexer, page_token_processor)


def parse_comment(comment):
    return parse(comment, CommentLexer, comment_token_processor)

