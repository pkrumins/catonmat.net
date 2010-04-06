#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug                           import Response
from catonmat.views.utils               import render_template

# ----------------------------------------------------------------------------

def main(request):
    template = render_template('404', path=request.path)
    return Response(template, mimetype='text/html', status=404)

