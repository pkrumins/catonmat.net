#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from sqlalchemy             import or_
from werkzeug.exceptions    import NotFound
from werkzeug               import redirect

from catonmat.database      import session, engine
from catonmat.models        import Page, UrlMap, TextAds
from catonmat.cache         import cache_del
from catonmat.config        import config
from catonmat.similarity    import related_posts
from catonmat.views.utils   import (
    MakoDict, cached_template_response, render_template, display_template,
    get_template
)
from catonmat.comments      import (
    validate_comment, new_comment, thread, linear, CommentError, lynx_browser
)

from datetime               import datetime

# ----------------------------------------------------------------------------

def main(request, map):
    if request.method == "POST":
        return handle_page_post(request, map)
    return handle_page_get(request, map)


def handle_page_post(request, map):
    # Currently POST can only originate from a comment being submitted.
    map = session.query(UrlMap).filter_by(url_map_id=map['url_map_id']).first()
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
        validate_comment(request, preview=True)
    except CommentError, e:
        return page_with_comment_error(request, map, e.message)

    comment = new_comment(request)
    comment_preview = (get_template('comment').
                         get_def('individual_comment').
                         render(comment=comment, preview=True))

    template_data = default_page_template_data(request, map)
    template_data['comment_data']['comment_preview'] = comment_preview

    return display_page(**template_data)


def page_with_comment_error(request, map, error):
    template_data = default_page_template_data(request, map)
    template_data['comment_data']['comment_error'] = error

    return display_page(**template_data)


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
        }),
        'related_posts':   related_posts(map.page),
        'lynx': lynx_browser(request)
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
        'display_short_url':     True,
        'display_series_after':  True,
        'display_related_posts': True,
        'display_social':        True,
        'display_bsa':           True,
    }

stackvm_ids = [226, 231, 245]

def handle_page_get(request, map):
    engine.execute("UPDATE pages SET views=views+1 WHERE page_id=%d" % map['page_id'])

    stackvm_post = False
    if map['page_id'] in stackvm_ids: # stackvm post ids
        stackvm_post = True

    if stackvm_post:
        su = request.args.get('signup')
        if su in ['ok', 'failed']:
            return compute_stackvm_get_page(request, map)

    return cached_template_response(
             compute_handle_page_get,
             'individual_page_%s' % map['request_path'],
             3600,
             request,
             map)


def compute_handle_page_get(request, map):
    map = session.query(UrlMap).filter_by(url_map_id=map['url_map_id']).first()
    template_data = default_page_template_data(request, map)
    text_ads = map.page.text_ads.filter(
                 or_(TextAds.expires==None, TextAds.expires<=datetime.utcnow())
               ).all()

    stackvm = False
    if map.page_id in stackvm_ids:
        stackvm=True

    return render_template("page",
            text_ads=text_ads,
            stackvm=stackvm,
            **template_data)


def compute_stackvm_get_page(request, map):
    map = session.query(UrlMap).filter_by(url_map_id=map['url_map_id']).first()
    template_data = default_page_template_data(request, map)
    text_ads = map.page.text_ads.filter(
                 or_(TextAds.expires==None, TextAds.expires<=datetime.utcnow())
               ).all()

    return display_page(
            text_ads=text_ads,
            stackvm=True,
            stackvm_signup=request.args.get('signup'),
            stackvm_signup_error=request.args.get('error'),
            **template_data
    )


def display_page(**template_data):
    return display_template("page", **template_data)

