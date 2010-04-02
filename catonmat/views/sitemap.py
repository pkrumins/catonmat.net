#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from catonmat.views.utils       import display_template
from catonmat.models            import Feedback

# ----------------------------------------------------------------------------

def main(request):
    return display_template("sitemap", dict())

