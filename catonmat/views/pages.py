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

from werkzeug.exceptions    import NotFound

from catonmat.views.utils   import render_template_with_quote
from catonmat.comments      import (
    add_comment, get_comment, thread, linear, CommentError
)
from catonmat.urls          import get_page_from_request_path
from catonmat.database      import Session
from catonmat.models        import Comment, Page, UrlMap

# ----------------------------------------------------------------------------

def main(request, map):
    comment_error = ""
    form = request.form

    if request.method == "POST":
        # TODO: if request.form.get('ajax')
        try:
            add_comment(request)
            form = dict()
            # TODO: after adding comment, redirect to this comment's page
        except CommentError, e:
            comment_error = e.message

    if request.args.get('linear') is not None:
        comment_mode = 'linear'
        comments = linear(map.page.comments.all())
    else:
        comment_mode = 'threaded'
        comments = thread(map.page.comments.all())

    template_data = {
        'page':                 map.page,
        'page_path':            map.request_path,
        'comment_submit_path':  map.request_path,
        'display_comments':     True,
        'comment_error':        comment_error,
        'form':                 form,
        'comments':             comments,
        'comment_mode':         comment_mode,
        'reply':                False
    }
    return render_template_with_quote("page", template_data)


def comment(request, id):
    if request.args.get('reply') is not None:
        return comment_reply(request, id)
    else:
        return comment_tree(request, id)


from catonmat.comments import validate_comment, new_comment
from catonmat.views.utils import get_template
from catonmat.database import Session
from werkzeug import redirect

def comment_reply(request, id):
    comment_error = None
    comment_preview = None
    form = dict()

    if request.method == "POST":
        print request.form
        if request.form.get('preview') is not None:
            form = request.form
            try:
                validate_comment(request)
                comment = new_comment(request)
                comment_preview = (get_template('comment').
                                     get_def('individual_comment').
                                     render(comment=comment, preview=True))
            except CommentError, e:
                comment_error = e.message
        elif request.form.get('submit') is not None:
            try:
                validate_comment(request)
                comment = new_comment(request)
                Session.add(comment)
                Session.commit()
                # TODO: redirect
                
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
        'reply':                True,
        'form':                 form,
        'comment_error':        comment_error,
        'comment_preview':      comment_preview
    }
    return render_template_with_quote("comment_page", template_data), 'text/html'


def comment_tree(request, root):
    # to be done
    return 'coming soon', 'text/html'
    pass

