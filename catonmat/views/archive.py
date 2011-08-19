#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from sqlalchemy                     import func
from werkzeug.exceptions            import NotFound
from calendar                       import month_name as MONTH

from catonmat.models                import Page, BlogPage
from catonmat.database              import session
from catonmat.views.utils           import (
    cached_template_response, render_template, number_to_us
)

# ----------------------------------------------------------------------------

def main(request):
    sorted_by = request.args.get('sorted_by', 'date')
    return cached_template_response(
             compute_main,
             'archive_%s' % sorted_by,
             3600,
             sorted_by)


def compute_main(sorted_by):
    if sorted_by == 'views':
        sort_f = Page.views.desc
    elif sorted_by == 'date':
        sort_f = BlogPage.publish_date.desc
    pages = session. \
              query(Page). \
              join(BlogPage). \
              order_by(sort_f()). \
              all()
    return render_template('archive',
        pages=pages,
        sorted_by=sorted_by,
        number_to_us=number_to_us)


def year(request, year):
    return cached_template_response(
             compute_year,
             'archive_year_%d' % year,
             3600,
             year)


def compute_year(year):
    pages = session. \
              query(Page). \
              join(BlogPage). \
              filter('year(blog_pages.publish_date) = %d' % year). \
              order_by(BlogPage.publish_date.desc()). \
              all()
    return render_template('archive_year',
             pages=pages,
             year=year,
             number_to_us=number_to_us)


def year_month(request, year, month):
    return cached_template_response(
             compute_year_month,
             'archive_year_month_%d_%d' % (year, month),
             3600,
             year,
             month)


def compute_year_month(year, month):
    filter_str = 'year(blog_pages.publish_date) = %d and ' \
                 'month(blog_pages.publish_date) = %d' % (year, month)
    pages = session. \
              query(Page). \
              join(BlogPage). \
              filter(filter_str). \
              order_by(BlogPage.publish_date.desc()). \
              all()
    return render_template('archive_year_month',
             pages=pages,
             year=year,
             nmonth=month,
             month=MONTH[month],
             number_to_us=number_to_us)

