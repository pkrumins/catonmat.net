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
from catonmat.models            import BlogPage, Page
from catonmat.database          import Session

# ----------------------------------------------------------------------------

def main(request):
    pages = (Session.
               query(Page).
               join(BlogPage).
               filter(BlogPage.visible==True).
               limit(config['posts_per_page']).
               offset(0).
               all())

    template_data = {
        'pages':    pages
    }
    return display_template_with_quote("index", template_data)

