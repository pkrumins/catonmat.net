#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#
# This file handles /c/<comment_id> short comment URLS.

from werkzeug               import redirect
from werkzeug.exceptions    import NotFound

from sqlalchemy             import join

from catonmat.cache         import cache_del
from catonmat.models        import Comment, Page, UrlMap
from catonmat.database      import session
from catonmat.views.utils   import get_template, display_template

from catonmat.comments      import (
    validate_comment,       new_comment, thread, CommentError,
    invalidate_page_cache
)

# ----------------------------------------------------------------------------

# TODO: add caching

def main(request, comment_id):
    if request.method == "POST":
        return handle_comment_post(request, comment_id)
    return handle_comment_get(request, comment_id)


def handle_comment_get(request, comment_id):
    if request.args.get('reply') is not None:
        return comment_reply(request, comment_id)
    return comment_tree(request, comment_id)


def default_comment_template_data(request, comment_id):
    mixergy = session. \
                query(Comment, Page, UrlMap). \
                join(Page, UrlMap). \
                filter(Comment.comment_id==comment_id). \
                first()

    if not mixergy:
        # TODO: "The requested comment was not found, here are a few latest coments"
        #       "Here are latest posts, here are most commented posts..."
        raise NotFound()

    comment, page, urlmap = mixergy

    template_data = {
        'page':                 page,
        'page_path':            urlmap.request_path,
        'comment_submit_path':  '/c/%d?reply' % comment_id,
        'comment_parent_id':    comment_id,
        'comment':              comment,
        'form':                 request.form,
    }
    return template_data


def comment_reply(request, comment_id):
    template_data = default_comment_template_data(request, comment_id)
    template_data['reply'] = True
    return display_page(template_data)


def comment_tree(request, comment_id):
    template_data = default_comment_template_data(request, comment_id)
    template_data['reply'] = False

    # TODO: optimize comment selection
    comments = thread(template_data['page'].comments.all())
    template_data['comments'] = comments

    return display_page(template_data)


def handle_comment_post(request, comment_id):
    if request.form.get('submit') is not None:
        return handle_comment_submit(request, comment_id)
    else:
        return handle_comment_preview(request, comment_id)


def comment_error(request, comment_id, error):
    template_data = default_comment_template_data(request, comment_id)
    template_data['comment_error'] = error
    template_data['reply'] = True

    return display_page(template_data)


def handle_comment_submit(request, comment_id):
    try:
        validate_comment(request)
    except CommentError, e:
        return comment_error(request, comment_id, e.message)

    comment = new_comment(request)
    comment.save()

    invalidate_page_cache(request.form['page_id'])

    return redirect('/c/%d' % comment.comment_id)


def handle_comment_preview(request, comment_id):
    try:
        validate_comment(request)
    except CommentError, e:
        return comment_error(request, comment_id, e.message)

    comment = new_comment(request)
    comment_preview = (get_template('comment').
                         get_def('individual_comment').
                         render(comment=comment, preview=True))

    template_data = default_comment_template_data(request, comment_id)
    template_data['comment_preview'] = comment_preview
    template_data['reply'] = True

    return display_page(template_data)


def display_page(template_data):
    return display_template("comment_page", **template_data)

