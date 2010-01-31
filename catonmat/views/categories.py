#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from sqlalchemy                     import join

from werkzeug.exceptions            import NotFound

from catonmat.views.utils           import display_template_with_quote
from catonmat.models                import Category, Page, UrlMap
from catonmat.database              import Session

# ----------------------------------------------------------------------------

def main(request, category):
    category = Category.query.filter_by(seo_name=category).first()
    if not category:
        raise NotFound()

    # TODO: select only the necessary fields
    mixergy = (Session.
                 query(Page, UrlMap).
                 join(UrlMap).
                 filter(Page.category_id==category.category_id).all())

    # TODO: add comment-count for each page, add excerpt, add publish date
    template_data = {
        'category':     category,
        'pus':          mixergy,
    }
    return display_page('category', template_data)


def list(request):
    categories = Category.query.all()
    template_data = {
        'categories': categories
    }
    return display_page('category_list', template_data)


def display_page(template, template_data):
    return display_template_with_quote(template, template_data)

