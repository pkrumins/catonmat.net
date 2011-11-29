#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug.exceptions        import NotFound

from catonmat.views.utils       import MakoDict, cached_template_response, render_template
from catonmat.database          import session
from catonmat.models            import Page, BlogPage, UrlMap
from catonmat.config            import config
from catonmat.cache             import cache

from math                       import ceil

# ----------------------------------------------------------------------------

class Pagination(object):
    def __init__(self, current_page, total_pages, items_per_page):
        self.current_page = current_page
        self.total_pages = total_pages
        self.items_per_page = items_per_page

    @property
    def physical_pages(self):
        return int(ceil(self.total_pages/(self.items_per_page + 0.0)))


def main(request):
    return handle_page()


def page(request, page_nr):
    blogpages = total_blogpages()
    last_page = int(ceil(blogpages/(config.posts_per_page + 0.0)))

    if page_nr <= 0 or page_nr > last_page:
        # TODO: display nice error that page is out of range,
        #       and point the user to latest posts, other interesting stuff.
        raise NotFound()

    return handle_page(page_nr)


def page_list(request):
    blogpages = total_blogpages()
    return cached_template_response(
             compute_page_list,
             'page_list',
             3600)


def compute_page_list():
    posts = session. \
              query(Page). \
              join(BlogPage). \
              order_by(BlogPage.publish_date.desc()). \
              filter(BlogPage.visible==True). \
              all()
    return render_template(
             'page_list',
             posts=posts,
             pagination=Pagination(1, total_blogpages(), config.posts_per_page))


def handle_page(page_nr=1):
    return cached_template_response(
             compute_handle_page,
             'index_page_%s' % page_nr,
             3600,
             page_nr)


def compute_handle_page(page_nr=1):
    mixergy = get_mixergy(page_nr)

    page_array = []
    for page, urlmap in mixergy:
        page_array.append(
            mako_page(page, urlmap.request_path)
        )

    template_data = {
        'page_array': page_array,
        'pagination': Pagination(page_nr, total_blogpages(), config.posts_per_page)
    }
    if page_nr == 1:
        template_data['front_page'] = True
    return render_template("index", **template_data)


@cache('total_blogpages')
def total_blogpages():
    return session. \
             query(BlogPage). \
             filter(BlogPage.visible==True). \
             count()


def get_mixergy(page=1):
    # TODO: narrow down the query
    return session. \
             query(Page, UrlMap). \
             join(BlogPage, UrlMap). \
             order_by(BlogPage.publish_date.desc()). \
             filter(BlogPage.visible==True). \
             limit(config.posts_per_page). \
             offset((page-1)*config.posts_per_page). \
             all() 


def default_display_options():
    return {
        'display_category':      True,
        'display_comment_count': True,
        'display_publish_time':  True,
        'display_tags':          False,
        'display_comments':      False,
        'display_comment_url':   True,
        'display_views':         True,
        'display_short_url':     False,
        'display_series_after':  False,
        'after_comments_ad':     False,
    }

    
def mako_page(page, request_path):
    return MakoDict({
        'page_data':        {
            'page':      page,
            'page_path': request_path
        },
        'comment_data':     {
            'comment_count': page.comment_count,
        },
        'display_options': default_display_options()
    })

