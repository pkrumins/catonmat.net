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

from StringIO               import StringIO
from urlparse               import urlparse
from collections            import defaultdict

import re
import simplejson as json

# ----------------------------------------------------------------------------

email_rx   = re.compile(r'^.+@.+\..+$')
twitter_rx = re.compile(r'^[a-zA-Z0-9_]+$')

class CommentError(Exception):
    pass


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

    def validate_twitter(twitter):
        if len(twitter) > 128:
            raise CommentError, "Your Twitter name is too long. Maximum length is 128 characters."
        
        if twitter:
            if not twitter_rx.match(twitter):
                raise CommentError, "Your Twitter name is incorrect! It can consist only of letters, numbers and underscore symbol."

    def validate_website(website):
        if len(website) > 256:
            raise CommentError, "Your website address is too long. Maximum length is 256 characters."

        if website:
            if '.' not in website:
                raise CommentError, "Your website address is invalid!"

            url = urlparse(website)
            if url.scheme:
                if url.scheme not in ('http', 'https', 'ftp'):
                    raise CommentError, "The only allowed Website schemes are http://, https:// and ftp://"

    def validate_page_id(page_id):
        number_of_pages = Page.query.filter_by(page_id=page_id).count()
        if number_of_pages != 1:
            raise CommentError, "Something went wrong, the page you were commenting on was not found..."

    def validate_parent_id(parent_id):
        if parent_id:
            comments = Comment.query.filter_by(comment_id=parent_id).count()
            if comments != 1:
                raise CommentError, "Something went wrong, the comment you were responding to was not found..."

    validate_page_id(request.form['page_id'])
    validate_parent_id(request.form['parent_id'])
    validate_name(request.form['name'].strip())
    validate_email(request.form['email'].strip())
    validate_twitter(request.form['twitter'].strip())
    validate_website(request.form['website'].strip())
    validate_comment(request.form['comment'].strip())


def preview_comment(request):
    if request.method == "POST":
        try:
            validate_comment(request)
        except CommentError, e:
            return json.dumps({
                'status':  'error',
                'message': e.message
            })

        return json.dumps({
            'status':  'success',
            'comment': get_template('comment').
                get_def('individual_comment').
                render(comment=new_comment(request))
        })


def add_comment(request):
    # TODO: make it work with web 1.0
    if request.method == "POST":
        validate_comment(request)

        comment = new_comment(request)
        Session.add(comment)
        Session.commit()


def get_comment(id):
    return Comment.query.filter_by(comment_id=id).first()


def new_comment(request):
    return Comment(
        page_id   = request.form['page_id'],
        parent_id = request.form['parent_id'],
        name      = request.form['name']   .strip(),
        comment   = request.form['comment'].strip(),
        email     = request.form['email']  .strip(),
        twitter   = request.form['twitter'].strip(),
        website   = request.form['website'].strip()
    )


def thread(comments):
    """
    Given a list of comments, threads them (creates a data structure
    that can be recursively iterated to output them in a threaded form).

    For example, for data:     it creates this tree:
    comment_id parent_id       root
    5          NULL            `-5
    6          5               | `-6
    7          5               | |`-8
    8          6               | `-7
    9          NULL            `-9 
    10         9               | `-10
    11         9               | |`-12
    12         10              | | `-13
    13         12              | `-11
    14         NULL            `-14

    and that tree is represented as the following data structure:
    {
      'root': [5, 9, 14],
      '5':    [6, 7],
      '6':    [8],
      '7':    [],        # actually keys with empty values are not present, i just added
      '8':    [],        # them here so that i can understand it better myself
      '9':    [10, 11],
      '10':   [12],
      '11':   [],
      '12':   [13],
      '13':   [],
      '14':   []
    }

    This data structure is actually the adjacency list representation of a graph.

    """
    
    ret = {'root': []}
    for comment in comments:
        if not comment.parent_id:
            ret['root'].append(comment)
        else:
            if comment.parent_id not in ret:
                ret[comment.parent_id] = []
            ret[comment.parent_id].append(comment)
    return ret


def linear(comments):
    return {'root': comments}

