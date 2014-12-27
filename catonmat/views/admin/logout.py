#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from catonmat.views.utils import display_plain_template
from catonmat.admin import require_admin

from werkzeug import Response

# ----------------------------------------------------------------------------

@require_admin()
def main(request):
    resp = Response('out', mimetype='text/plain')
    resp.delete_cookie('admin')
    return resp

