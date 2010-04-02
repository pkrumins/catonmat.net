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

from catonmat.database      import session
from catonmat.models        import Page
from catonmat.cache         import cache_del
from catonmat.config        import config
from catonmat.views.utils   import (
    MakoDict, cached_template_response, render_template, display_template
)
from catonmat.comments      import (
    validate_comment, new_comment, thread, linear, CommentError
)

# ----------------------------------------------------------------------------

def main(request, map):
    map = session.merge(map)
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
    comment.save()

    if config.use_cache:
        cache_del('individual_page_%s' % map.request_path)
    
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
    plain_old_comments = map.page.comments.all()
    if request.args.get('linear') is not None:
        comment_mode = 'linear'
        comments = linear(plain_old_comments)
    else:
        comment_mode = 'threaded'
        comments = thread(plain_old_comments)

    return {
        'display_options': MakoDict(default_display_options()),
        'page_data':       MakoDict({
            'page':                 map.page,
            'page_path':            map.request_path
        }),
        'comment_data':    MakoDict({
            'comment_count':        len(plain_old_comments),
            'comments':             comments,
            'comment_submit_path':  map.request_path,
            'comment_mode':         comment_mode,
            'form':                 request.form,
        }, ['comments', 'form']),
        'tags_data':       MakoDict({
            'tags':                 map.page.tags
        })
    }


def default_display_options():
    return {
        'display_category':      True,
        'display_comment_count': True,
        'display_publish_time':  True,
        'display_comments':      True,
        'display_comment_url':   True,
        'display_tags':          True,
        'display_views':         True,
        'display_short_url':     True
    }


def handle_page_get(request, map):
    map.page.views = Page.views + 1
    map.page.save()
    return cached_template_response(
             compute_handle_page_get,
             'individual_page_%s' % map.request_path,
             3600,
             request,
             map)


def compute_handle_page_get(request, map):
    template_data = default_page_template_data(request, map)
    return render_template("page", **template_data)


def display_page(template_data):
    return display_template("page", template_data)

