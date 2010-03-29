#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug             import Request, redirect
from werkzeug.exceptions  import HTTPException, NotFound
from werkzeug             import SharedDataMiddleware

from catonmat.database    import session
from catonmat.urls        import url_map, get_page_from_request_path
from catonmat.views.utils import get_view
from catonmat.fourofour   import log_404

from os import path

# ----------------------------------------------------------------------------

def handle_request(view, *values, **kw_values):
    handler = get_view(view)
    return handler(*values, **kw_values)


@Request.application
def application(request):
    try:
        adapter = url_map.bind_to_environ(request.environ)
        endpoint, values = adapter.match()
        return handle_request(endpoint, request, **values)
    except NotFound:
        map = get_page_from_request_path(request.path)
        if map:
            if map.redirect:
                return redirect(map.redirect, code=301)

            if map.page:
                return handle_request('pages.main', request, map)

            if map.handler:
                return handle_request(map.handler, request, map)

        # Log this request in the 404 log and display not found page
        log_404(request)
        return handle_request('not_found.main', request)
    except HTTPException, e:
        # TODO: log http exception so that I knew exactly what is going on with catonmat!
        print "HTTPException"
        pass
    finally:
        session.remove()

application = SharedDataMiddleware(application,
    { '/static': path.join(path.dirname(__file__), 'static') }
)

