#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from catonmat.views.utils       import (
    MakoDict, cached_template_response, render_template
)

# ----------------------------------------------------------------------------

# TODO: make this dynamic

PAGES_D = [
    { 'path': '/projects', 'name': 'Projects', 'title': "Peteris Krumins' projects" },
    { 'path': '/sitemap',  'name': 'Sitemap',  'title': "Catonmat sitemap" },
    { 'path': '/feedback', 'name': 'Feedback', 'title': "Contact Peteris Krumins" }
]

PAGES = [ MakoDict(d) for d in PAGES_D ]

def main(request):
    return cached_template_response(compute_sitemap, 'sitemap', 0)


def compute_sitemap():
    return render_template('sitemap', pages=PAGES)

