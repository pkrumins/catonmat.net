#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug.exceptions        import BadRequest

from catonmat.views.utils       import display_template_with_quote, MakoDict
from catonmat.config            import config
from catonmat.models            import BlogPage, Page, UrlMap
from catonmat.database          import Session

from math                       import ceil

# ----------------------------------------------------------------------------

def main(request):
    return handle_page()


def page(request, page_nr):
    blogpages = total_blogpages()
    last_page = int(ceil(blogpages/(config['posts_per_page'] + 0.0)))

    if page_nr <= 0 or page_nr > last_page:
        # TODO: display nice error that page is out of range,
        #       and point the user to latest posts, other interesting stuff.
        raise BadRequest()

    return handle_page(page_nr)


class Pagination(object):
    def __init__(self, current_page, total_pages, items_per_page):
        self.current_page = current_page
        self.total_pages = total_pages
        self.items_per_page = items_per_page

    @property
    def physical_pages(self):
        return int(ceil(self.total_pages/(self.items_per_page + 0.0)))


def handle_page(page_nr=1):
    # cached_page = get_cached_page("index", page_nr)
    mixergy = get_mixergy(page_nr)

    page_array = []
    for page, urlmap in mixergy:
        page_array.append(
            mako_page(page, urlmap.request_path)
        )

    template_data = {
        'page_array': page_array,
        'pagination': Pagination(page_nr, total_blogpages(), config['posts_per_page'])
    }
    return display_template_with_quote("index", template_data)


def total_blogpages():
    return BlogPage.query.count()


def get_mixergy(page=1):
    # TODO: narrow down the query
    mixergy = (Session.  
                query(Page, UrlMap). 
                join(BlogPage, UrlMap). 
                order_by(BlogPage.publish_date.desc()). 
                filter(BlogPage.visible==True).  
                limit(config['posts_per_page']). 
                offset((page-1)*config['posts_per_page']). 
                all())
    return mixergy


def default_display_options():
    return {
        'display_category':      True,
        'display_comment_count': True,
        'display_publish_time':  True,
        'display_tags':          False,
        'display_comments':      False
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

