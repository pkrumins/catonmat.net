#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# Code is licensed under MIT license.
#

from catonmat.database          import session
from catonmat.models            import Page, Download, BlogPage

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

