#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#
# This file handles /p/<page_id> short page URLS.

from werkzeug               import redirect
from werkzeug.exceptions    import NotFound

from catonmat.models        import UrlMap

# ----------------------------------------------------------------------------

def main(request, page_id):
    return redirect(find_url(page_id), code=301)


def find_url(page_id):
    map = UrlMap.query.filter_by(page_id=page_id).first()
    if not map:
        # TODO: 'page you were looking for was not found, perhaps you want to see ...'
        raise NotFound()
    return map.request_path

