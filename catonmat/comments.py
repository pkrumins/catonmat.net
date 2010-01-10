#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug               import redirect
from werkzeug.exceptions    import BadRequest

from catonmat.models        import Page, Comment, UrlMap
from catonmat.database      import Session
from catonmat.views.utils   import get_template

from pygments.lexer         import RegexLexer
from pygments.token         import Token, Whitespace, Text
from pygments               import format, lex

from StringIO               import StringIO

import re
import simplejson as json

# ----------------------------------------------------------------------------

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
    return comment

    tokenstream = lex(comment, CommentLexer())
    outfile = StringIO()
    for token, value in tokenstream:
        if token is Error:
            # todo, can't trust the comment anymore, html escape everything
            raise ParseError, "Failed parsing the comment"
        if token is Tag.Open:
            outfile.write("&lt;")
        elif token is Text.Par:
            outfile.write("\n<p>")
        else:
            outfile.write(value)
    return outfile.getvalue()


def validate_comment(request):
    def validate_name(name):
        if not name:
            raise CommentError, "You forgot to specify your name!"
        if len(name) > 64:
            raise CommentError, "Your name is too long. Maximum length is 64 characters."

    def validate_email(email):
        if email:
            if not email_rx.match(email):
                raise CommentError, "Sorry, the e-mail address is not valid!"
            if len(email) > 128:
                raise CommentError, "Your e-mail is too long. Maximum length is 128 characters."

    def validate_comment(comment):
        if not comment:
            raise CommentError, "You left the comment empty!"

    def validate_page_id(page_id):
        number_of_pages = Page.query.filter_by(page_id=request.form['page_id']).count()
        if number_of_pages != 1:
            raise CommentError, "Something went wrong, the page was not found..."

    def validate_twitter(twitter):
        if len(twitter) > 128:
            raise CommentError, "Your Twitter name is too long. Maximum length is 128 characters."

    def validate_website(website):
        if len(website) > 256:
            raise CommentError, "Your website address is too long. Maximum length is 256 characters."

    validate_name(request.form['name'].strip())
    validate_email(request.form['email'].strip())
    validate_comment(request.form['comment'].strip())
    validate_twitter(request.form['twitter'].strip())
    validate_website(request.form['website'].strip())
    validate_page_id(request.form['page_id'])


def preview_comment(request):
    if request.method == "POST":
        try:
            validate_comment(request)
            comment = parse_comment(request.form['comment'])
        except CommentError, e:
            return json.dumps({
                'status':  'error',
                'message': e.message
            })
        # TODO: this is not right:
        #except ParseError, e:
        #    return json.dumps({
        #        'status':  'error',
        #        'message': e.message
        #    })

        return json.dumps({
            'status':  'success',
            'comment': get_template('comment').
                get_def('individual_comment').
                render(comment=new_comment(request))
        })


def add_comment(request):
    if request.method == "POST":
        validate_comment(request)

        comment = new_comment(request)
        Session.add(comment)
        Session.commit()


def get_comment(id):
    return Comment.query.filter_by(comment_id=id).first()

def new_comment(request):
    return Comment(
            request.form['page_id'],
            request.form['name'].strip(),
            request.form['comment'].strip(),
            request.form['email'].strip(),
            request.form['twitter'].strip(),
            request.form['website'].strip())

