#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug.exceptions    import BadRequest
from catonmat.models        import Page

from pygments.lexer         import RegexLexer
from pygments.token         import *
from pygments               import format, lex

from StringIO               import StringIO

import re

email_rx = re.compile(r'^.+@.+\..+$')

Tag = Token.Tag

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


class CommentError(Exception):
    pass


class ParseError(CommentError):
    pass


def parse_comment(comment):
    tokenstream = lex(comment, CommentLexer())
    outfile = StringIO()
    for token, value in tokenstream:
        if token is Error:
            raise ParseError, "Failed parsing the comment"
        if token is Tag.Open:
            outfile.write("&lt;")
        elif token is Text.Par:
            outfile.write("\n<p>")
        else:
            outfile.write(value)
    return outfile.getvalue()


def validate_comment(request):
    if not len(request.form['name'].strip()):
        raise CommentError, "No name specified."
    if not len(request.form['email'].strip()):
        raise CommentError, "No e-mail specified."
    if not email_rx.match(request.form['email'].strip()):
        raise CommentError, "Invalid e-mail address specified."
    if not len(request.form['comment'].strip()):
        raise CommentError, "The comment is empty."


    number_of_pages = Page.query.filter_by(
            page_id=request.form['page_id']).count()

    if number_of_pages != 1:
        raise BadRequest

