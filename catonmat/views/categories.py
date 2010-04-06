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
from catonmat.models                import Category, BlogPage
from catonmat.database              import session
from catonmat.views.utils           import (
    cached_template_response, render_template, number_to_us
)

# ----------------------------------------------------------------------------

def main(request, seo_name):
    return cached_template_response(
             compute_main,
             'category_page_%s' % seo_name,
             3600,
             request,
             seo_name)

def compute_main(request, seo_name):
    category = session.query(Category).filter_by(seo_name=seo_name).first() 
    if not category:
        raise NotFound()

    pages = category.blog_pages.order_by(BlogPage.publish_date.desc()).all()

    return render_template('category', category=category, pages=pages,
             number_to_us=number_to_us)


def list(request):
    return cached_template_response(
             compute_list,
             'category_list',
             3600,
             request)


def compute_list(request):
    return render_template('category_list')

