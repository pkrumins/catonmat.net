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
from pygments.token         import Token, Text, Comment, Error, Whitespace
from pygments               import format, lex

from StringIO               import StringIO
from urlparse               import urlparse

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
    allowed_a_schemes = frozenset(['http', 'https', 'ftp'])
    def a_href_checker(lexer, match):
        href = match.group(1).strip()
        url = urlparse(href)

        if not url.scheme:
            href = 'http://' + href
        else:
            if url.scheme not in CommentLexer.allowed_a_schemes:
                yield match.start(), Error, "URL scheme %s is not allowed." % url.scheme
            else:
                yield match.start(), Text.A.Href, 'href="%s"' % href

    def code_lang_checker(lexer, match):
        yield match.start(), Text.Code.Lang, match.group(0)

    def latex_handler(lexer, match):
        latex = match.group(1).strip()
        google_url = 'http://chart.apis.google.com/chart?cht=tx&chf=bg,s,FFFFFF00&chco=222222&chl='
        url = google_url + latex
        yield match.start(), Tag.Latex, '<img src="%s" class="latex" height="12">' % url

    flags = re.IGNORECASE | re.DOTALL
    tokens = {
        'root': [
            (r'\n\n',       Text.Par),
            (r'\n',         Text.Br),
            (r'[^<\n]+',    Text),
            (r'<(b|i|q)>',  Tag.Allowed.Open),
            (r'<a',         Tag.Allowed.Open, 'a'),
            (r'<code',      Tag.Allowed.Open, 'code'),
            (r'<latex>(.+?)</latex>', latex_handler),
            (r'</(a|code|b|i|q)>', Tag.Allowed.Close),
            (r'<',          Tag.Unknown.Open)
        ],
        'a': [
            (r'\s+',            Whitespace),
            (r'href="([^"]+)"', a_href_checker),
            (r"href='([^']+)'", a_href_checker),
            (r'>',              Tag.Close, '#pop')
        ],
        'code': [
            (r'\s+',            Whitespace),
            (r'lang="([^"]+)"', code_lang_checker),
            (r"lang='([^']+)'", code_lang_checker),
            (r'>',              Tag.Close, '#pop')
        ],
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


class PageState(object):
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
        a = self.in_tag() not in PageState.inline_tags
        b = self.in_tag() not in PageState.dont_p
        return a and b

    def in_tag(self):
        if self.in_tags:
            return self.in_tags[-1]
        return None

    def enter_tag(self, tag):
        if tag not in PageState.self_closing_tags:
            self.in_tags.append(tag)

    def leave_tag(self):
        try:
            self.in_tags.pop()
        except IndexError:
            pass


class CommentState(object):
    pass


def extract_tag_name(value):
    matches = re.match(r'<\s*([a-zA-Z0-9:]+)', value)
    if matches:
        return matches.group(1)
    raise ValueError("Tag '%s' didn't match regex" % value)


def page_token_processor(state, token, value, prev_token, next_token):
    """ Process a (token, value) based on prev_token, next_token and current state """

    # Pygments has a nasty feature that it adds a newline at the end,
    # the following tests if it's this is the last token and if it's newline,
    # then don't process it.
    if next_token is None and token is Text.Br:
        return ''
    
    if token is Text:
        if not state.par_started:
            if state.should_p():
                state.par_started = True
                return "<p>" + value
        return value

    if token is Tag.Open:
        tag = extract_tag_name(value)
        state.enter_tag(tag)
        return value

    if token is Tag.Close:
        state.leave_tag()

    if token is Text.Par:
        state.par_started = False

    if token is Text.Br:
        if prev_token is Tag.Text:
            return "<br>"

    if token is Error:
        return "<span style=\"color: red; font-size: 2em\">Error: " + value + "</span>"

    return value


def comment_token_processor(state, token, value, prev_token, next_token):
    """ Process a (token, value) based on prev_token, next_token and current state """

    # Pygments has a nasty feature that it adds a newline at the end,
    # the following tests if it's this is the last token and if it's newline,
    # then don't process it.
    if next_token is None and token is Text.Br:
        return ''

    if token is Tag.Unknown.Open:
        if prev_token is None:
            return '<p>&lt;'
        return '&lt;'

    if token is Text.Par:
        return '\n<p>'

    if token is Text.Br:
        return '<br>'

    if token is Error:
        # TODO: better error handling
        return ''

    if prev_token is None:
        return '<p>' + value
    else:
        return value


def build_html(tokenstream, token_processor, state_keeper):
    outfile = StringIO()
    state = state_keeper()
    prev_token = None

    for token, value in tokenstream:
        try:
            next_token, _ = tokenstream.peek()
        except StopIteration:
            next_token = None

        outfile.write(token_processor(state, token, value, prev_token, next_token))
        prev_token = token

    return outfile.getvalue()


def parse(text, lexer, processor, state_keeper):
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = re.sub(r'\n\n+', '\n\n', text)

    tokenstream = GeneratorWithPeek(lex(text, lexer()))
    return build_html(tokenstream, processor, state_keeper)


def parse_page(page):
    return parse(page, PageLexer, page_token_processor, PageState)


def parse_comment(comment):
    return parse(comment, CommentLexer, comment_token_processor, CommentState)

