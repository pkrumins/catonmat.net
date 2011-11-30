#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from catonmat.views.utils   import display_template

# ----------------------------------------------------------------------------

def main(request, url):
    fixed_url = "/" + url
    return display_template("mobile_page", page_url=fixed_url)

