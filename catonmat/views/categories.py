#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug.exceptions            import NotFound
from catonmat.models                import Category, Page, UrlMap
from catonmat.database              import session
from catonmat.views.utils           import cached_template_response, render_template

# ----------------------------------------------------------------------------

def main(request, seo_name):
    return cached_template_response(
             'category_page_%s' % seo_name,
             compute_main,
             request,
             seo_name)

def compute_main(request, seo_name):
    category = session.query(Category).filter_by(seo_name=seo_name).first() 
    if not category:
        raise NotFound()

    # TODO: select only the necessary fields
    mixergy = session. \
                query(Page, UrlMap). \
                join(UrlMap). \
                filter(Page.category_id==category.category_id). \
                all() 

    # TODO: add comment-count for each page, add excerpt, add publish date
    template_data = {
        'category':     category,
        'pus':          mixergy,
    }
    return render_template('category', **template_data)


def list(request):
    return cached_template_response(
             'category_list',
             compute_list,
             request)

def compute_list(request):
    categories = session.query(Category).order_by(Category.name).all() 
    template_data = {
        'categories': categories
    }
    return render_page('category_list', **template_data)

