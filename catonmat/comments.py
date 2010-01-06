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

allowed_tags = ['b', 'i', 'q', 'a', 'code']

Tag = Token.Tag

class CommentLexer(RegexLexer):
    flags = re.IGNORECASE | re.DOTALL
    tokens = {
        'tags': [
            (r'<(b|i|q)>',  Tag.Allowed),
            (r'<a',         Tag.Allowed, 'a'),
            (r'<code',      Tag.Allowed, 'code'),
            (r'<',          Tag.Unknown)
        ],
        'a': [
            (r'\s*',        WhiteSpace),
            (r'')
        ],
        'root': [
            (r'\n\n', Text.Par),
            (r'[^<\n]+', Text),
            include('tags'),
        ],
        'comment': [
            (r'[^-]+', Comment),
            (r'-->',   Comment, '#pop'),
            (r'-',     Comment),
        ],
        'tag': [
            (r'[^>]+', Tag.Contents),
            (r'>',     Tag.End, '#pop'),
        ],
    }


class CommentError(Exception):
    pass


class ParseError(CommentError):
    pass


def parse_comment(comment):

    return comment


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

