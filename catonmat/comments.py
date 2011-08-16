#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug               import redirect, Response
from werkzeug.exceptions    import BadRequest

from catonmat.config        import config
from catonmat.cache         import cache_del
from catonmat.models        import Page, Comment, Visitor
from catonmat.database      import session
from catonmat.views.utils   import get_template

from StringIO               import StringIO
from urlparse               import urlparse
from collections            import defaultdict

import re
import simplejson as json

from comment_spamlist import spamlist_names, spamlist_urls, spamlist_comments

# ----------------------------------------------------------------------------

email_rx   = re.compile(r'^.+@.+\..+$')
twitter_rx = re.compile(r'^[a-zA-Z0-9_]+$')
lynx_re  = re.compile(r'Lynx|Links', re.I)

def lynx_browser(request):
    browser = request.headers.get('User-Agent')
    if browser:
        if lynx_re.match(browser):
            return True
    return False


class CommentError(Exception):
    pass


def validate_comment(request, preview=False):
    def validate_name(name):
        if not name:
            raise CommentError, "You forgot to specify your name!"
        if len(name) > 64:
            raise CommentError, "Your name is too long. Maximum length is 64 characters."

    def validate_email(email):
        if email:
            if len(email) > 128:
                raise CommentError, "Your e-mail is too long. Maximum length is 128 characters."
            if not email_rx.match(email):
                raise CommentError, "Sorry, your e-mail address is not valid!"

    def validate_comment_txt(comment):
        if not comment:
            raise CommentError, "You left the comment empty!"

    def validate_twitter(twitter):
        if twitter:
            if len(twitter) > 128:
                raise CommentError, "Your Twitter name is too long. Maximum length is 128 characters."
            if not twitter_rx.match(twitter):
                raise CommentError, "Your Twitter name is incorrect! It can consist only of letters, numbers and the underscore symbol."

    def validate_website(website):
        if website:
            if len(website) > 256:
                raise CommentError, "Your website address is too long. Maximum length is 256 characters."
            if '.' not in website:
                raise CommentError, "Your website address is invalid!"

            url = urlparse(website)
            if url.scheme:
                if url.scheme not in ('http', 'https', 'ftp'):
                    raise CommentError, "The only allowed website schemes are http://, https:// and ftp://"

    def validate_page_id(page_id):
        number_of_pages = session.query(Page).filter_by(page_id=page_id).count()
        if number_of_pages != 1:
            raise CommentError, "Something went wrong, the page you were commenting on was not found..."

    def validate_parent_id(parent_id):
        if parent_id:
            comments = session.query(Comment).filter_by(comment_id=parent_id).count()
            if comments != 1:
                raise CommentError, "Something went wrong, the comment you were responding to was not found..."

    def validate_captcha(name, captcha):
        if name[0:3] != captcha:
            raise CommentError, 'Please type "' + name[0:3] + '" in the box below'

    def validate_spam_comment(name, url, comment):
        msg = """My anti-spam system says your comment looks spammy. I can't post it. If you're a real person and your comment is real, can you please email it to me at <a href="mailto:peter@catonmat.net">peter@catonmat.net</a>? I'll post your comment then and tune my anti-spam system not to match comments like these in the future. Thanks!"""

        for r in spamlist_names:
            if r.search(name):
                raise CommentError, msg

        for r in spamlist_urls:
            if r.search(url):
                raise CommentError, msg

        for r in spamlist_comments:
            if r.search(comment):
                raise CommentError, msg

    validate_page_id(request.form['page_id'])
    validate_parent_id(request.form['parent_id'])
    validate_name(request.form['name'].strip())
    validate_email(request.form['email'].strip())
    validate_twitter(request.form['twitter'].replace('@', '').strip())
    validate_website(request.form['website'].strip())
    validate_comment_txt(request.form['comment'].strip())
    validate_spam_comment(request.form['name'].strip(), request.form['website'].strip(), request.form['comment'].strip())

    if not lynx_browser(request) and not preview:
        validate_captcha(request.form['name'].strip(), request.form['commentc'].strip())


def json_response(**data):
    return json.dumps(data)


# TODO: @json_response
def preview_comment(request):
    if request.method == "POST":
        try:
            validate_comment(request, preview=True)
        except CommentError, e:
            return Response(json_response(status='error', message=e.message)
                 ,   mimetype='application/json')

        return Response(
                json_response(status='success',
                    comment=get_template('comment').
                            get_def('individual_comment').
                            render(comment=new_comment(request),
                    preview=True))
        , mimetype='application/json')


def add_comment(request):
    if request.method == "POST":
        try:
            validate_comment(request)
        except CommentError, e:
            return Response ( json_response(status='error', message=e.message)
                    , mimetype='application/json')

        comment = new_comment(request)
        comment.save()

        invalidate_page_cache(request.form['page_id'])

        return Response(
                json_response(status='success',
                    comment=get_template('comment').
                            get_def('individual_comment').
                            render(comment=comment))
        , mimetype='application/json')


def invalidate_page_cache(page_id):
    if config.use_cache:
        page = session.query(Page).filter_by(page_id=page_id).first()
        cache_del('individual_page_%s' % page.request_path)


def get_comment(id):
    return session.query(Comment).filter_by(comment_id=id).first()


def new_comment(request):
    return Comment(
        page_id   = request.form['page_id'],
        parent_id = request.form['parent_id'],
        name      = request.form['name']   .strip(),
        comment   = request.form['comment'].strip(),
        email     = request.form['email']  .strip(),
        twitter   = request.form['twitter'].replace('@', '').strip(),
        website   = request.form['website'].strip(),
        visitor   = Visitor(request)
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
    """
    Given a list of comments, returns them in linear order (to display them as
    a simple list and not as a threaded tree.
    """

    return {'root': comments}

