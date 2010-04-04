#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# Code is licensed under MIT license.
#

from catonmat.database          import session
from catonmat.models            import Page, Download, BlogPage

from sqlalchemy                 import func
from calendar                   import month_name as MONTH


# ----------------------------------------------------------------------------

def get_most_popular_pages(count=10):
    return session. \
             query(Page). \
             join(BlogPage). \
             order_by(Page.views.desc()). \
             limit(count). \
             all()


def get_most_downloads(count=10):
    return session. \
             query(Download). \
             order_by(Download.downloads.desc()). \
             limit(count). \
             all()


def get_recent_pages(count=10):
    return session. \
             query(Page). \
             join(BlogPage). \
             order_by(BlogPage.publish_date.desc()). \
             limit(count). \
             all()


def get_post_archive():
    fy = func.year
    fm = func.month
    bp = BlogPage.publish_date
    ymc = session. \
             query(fy(bp), fm(bp), func.count()). \
             group_by(fy(bp), fm(bp)). \
             order_by(fy(bp).desc()). \
             order_by(fm(bp).desc()). \
             all()
    for y, m, c in ymc:
        yield y, MONTH[m], c

