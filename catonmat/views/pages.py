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
from werkzeug               import redirect

from catonmat.views.utils   import get_template, display_template_with_quote
from catonmat.comments      import (
    validate_comment, new_comment, save_comment, thread, linear, CommentError
)

# ----------------------------------------------------------------------------

def main(request, map):
    if request.method == "POST":
        return handle_page_post(request, map)
    return handle_page_get(request, map)


def handle_page_post(request, map):
    # Currently POST can only originate from a comment being submitted.
    if request.form.get('submit') is not None:
        return handle_comment_submit(request, map)

    if request.form.get('preview') is not None:
        return handle_comment_preview(request, map)

    raise NotFound()


def handle_comment_submit(request, map):
    try:
        validate_comment(request)
    except CommentError, e:
        return page_with_comment_error(request, map, e.message)

    # TODO: merge this, c.py and comments.py together,
    #       otherwise same code is spread over 3 files
    comment = new_comment(request)
    save_comment(comment)

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
    template_data['comment_preview'] = comment_preview

    return display_page(template_data)


def page_with_comment_error(request, map, error):
    template_data = default_page_template_data(request, map)
    template_data['comment_error'] = error
    
    return display_page(template_data)


def default_page_template_data(request, map):
    if request.args.get('linear') is not None:
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
        'comment_mode':         comment_mode,
        'comment_count':        map.page.comment_count,
        'tags':                 map.page.tags
    }


def handle_page_get(request, map):
    return display_page(default_page_template_data(request, map))


def display_page(template_data):
    return display_template_with_quote("page", template_data)

