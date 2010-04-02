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
    if request.method == "POST":
        return handle_feedback_post(request)
    return handle_feedback_get(request)


def handle_feedback_post(request):
    return display_template("feedback", dict())


def handle_feedback_get(request):
    return display_template("feedback", dict())

