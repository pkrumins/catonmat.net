#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug.exceptions    import NotFound
from werkzeug               import Response

from catonmat.views.utils   import display_template_with_quote
from catonmat.comments      import (
    add_comment, get_comment, thread, linear, CommentError
)
from catonmat.urls          import get_page_from_request_path
from catonmat.database      import Session
from catonmat.models        import Comment, Page, UrlMap

# ----------------------------------------------------------------------------

from catonmat.comments import validate_comment, new_comment
from catonmat.views.utils import get_template
from catonmat.database import Session
from werkzeug import redirect

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main(request, map):
    if request.method == "POST":
        return handle_page_post(request, map)
    return handle_page_get(request, map)


def handle_page_post(request, map):
    # Currently POST can only originate from a comment being submitted.
    if request.form.get('submit'):
        return handle_comment_submit(request, map)

    if request.form.get('preview'):
        return handle_comment_preview(request, map)

    raise NotFound()


def handle_comment_submit(request, map):
    try:
        validate_comment(request)
    except CommentError, e:
        return page_with_comment_error(request, map, e.message)

    comment = new_comment(request)
    Session.add(comment)
    Session.commit()

    return redirect('/c/%d' % comment.comment_id)


def handle_comment_preview(request, map):
    try:
        validate_comment(request)
    except CommentError, e:
        return page_with_comment_error(request, map, e.message)

    comment = new_comment(request)
    comment_preview = (get_template('comment').
                         get_def('individual_comment').
                         render(comment=comment, preview=True))

    template_data = default_page_template_data(request, map)
    new_data = {
        'comment_preview': comment_preview
    }
    template_data.update(new_data)

    return display_page(template_data)


def page_with_comment_error(request, map, error):
    template_data = default_page_template_data(request, map)
    new_data = {
        'comment_error': error,
    }
    template_data.update(new_data)
    
    return display_page(template_data)


def default_page_template_data(request, map):
    if request.args.get('linear'):
        comment_mode = 'linear'
        comments = linear(map.page.comments.all())
    else:
        comment_mode = 'threaded'
        comments = thread(map.page.comments.all())

    return {
        'page':                 map.page,
        'page_path':            map.request_path,
        'comment_submit_path':  map.request_path,
        'display_comments':     True,
        'form':                 request.form,
        'comments':             comments,
        'comment_mode':         comment_mode
    }


def handle_page_get(request, map):
    return display_page(default_page_template_data(request, map))


def display_page(template_data):
    return display_template_with_quote("page", template_data)


# ------------------
# /c/<id>
#

def comment(request, id):
    if request.args.get('reply') is not None:
        return comment_reply(request, id)
    else:
        return comment_tree(request, id)


def comment_reply(request, id):
    comment_error = None
    comment_preview = None
    form = request.form

    if request.method == "POST":
        if request.form.get('submit') is not None:
            try:
                validate_comment(request)
                comment = new_comment(request)
                Session.add(comment)
                Session.commit()
                return redirect('/c/%d' % id)
            except CommentError, e:
                comment_error = e.message
        elif request.form.get('preview') is not None:
            try:
                validate_comment(request)
                comment = new_comment(request)
                comment_preview = (get_template('comment').
                                     get_def('individual_comment').
                                     render(comment=comment, preview=True))
            except CommentError, e:
                comment_error = e.message

    mixergy = (Session.
                 query(Comment, Page, UrlMap).
                 join(Page, UrlMap).
                 filter(Comment.comment_id==id).
                 first())

    if not mixergy:
        # TODO: "The requested comment was not found, here are a few latest coments"
        #       "Here are latest posts, here are most commented posts..."
        raise NotFound()

    comment, page, urlmap = mixergy

    template_data = {
        'comment':              comment,
        'page':                 page,
        'page_path':            urlmap.request_path,
        'comment_submit_path':  '/c/%d?reply' % id,
        'comment_parent_id':    id,
        'form':                 form,
        'comment_error':        comment_error,
        'comment_preview':      comment_preview,
        'reply':                True
    }
    return display_template_with_quote("comment_page", template_data)


def comment_tree(request, id):
    # to be done
    # return Response('coming soon', mimetype='text/html')

    mixergy = (Session.
                 query(Comment, Page, UrlMap).
                 join(Page, UrlMap).
                 filter(Comment.comment_id==id).
                 first())

    if not mixergy:
        # TODO: "The requested comment was not found, here are a few latest coments"
        #       "Here are latest posts, here are most commented posts..."
        raise NotFound()

    comment, page, urlmap = mixergy

    comments = thread(page.comments.all())

    template_data = {
        'page':                 page,
        'page_path':            urlmap.request_path,
        'comment_submit_path':  '/c/%d?reply' % id,
        'comment_parent_id':    id,
        'comment_error':        None,
        'comment_preview':      None,
        'form':                 dict(),
        'comment':              comment,
        'comments':             comments,
        'reply':                False
    }
    return display_template_with_quote("comment_page", template_data)

