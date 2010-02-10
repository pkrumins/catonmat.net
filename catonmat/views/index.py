#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from catonmat.views.utils       import display_template_with_quote
from catonmat.config            import config
from catonmat.models            import BlogPage, Page, UrlMap
from catonmat.database          import Session

# ----------------------------------------------------------------------------

def main(request):
    # TODO: narrow down the query
    mixergy = (Session.
                 query(Page, UrlMap).
                 join(BlogPage, UrlMap).
                 order_by(BlogPage.publish_date).
                 filter(BlogPage.visible==True).
                 limit(config['posts_per_page']).
                 offset(0).
                 all())

    template_data = {
        'mixergy':    mixergy
    }
    return display_template_with_quote("index", template_data)


def page(request, page_nr):
    pass

