#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website. See this post for more info:
# http://www.catonmat.net/blog/50-ideas-for-the-new-catonmat-website/
#
# Code is licensed under GNU GPL license.
#

from os import path

from werkzeug             import Request, Response, import_string
from werkzeug.exceptions  import HTTPException, NotFound
from werkzeug             import SharedDataMiddleware

from catonmat.database    import Session
from catonmat.urls        import url_map, get_page_from_request_path
from catonmat.views.utils import get_view
from catonmat.fourofour   import log_404

# ----------------------------------------------------------------------------

def handle_request(request, endpoint, values=None, mimetype='text/html'):
    if values is None: values = {}
    handler = get_view(endpoint)
    content = handler(request, **values)
    return Response(content, mimetype=mimetype)

@Request.application
def application(request):
    try:
        adapter = url_map.bind_to_environ(request.environ)
        endpoint, values = adapter.match()
        return handle_request(request, endpoint, values)
    except NotFound:
        map = get_page_from_request_path(request.path)
        if map:
            if map.handler:
                handler = get_view(map.handler)
                content = handler(request, map)
                return Response(content, mimetype='text/html')
            elif map.page:
                handler = get_view('pages.main')
                content = handler(request, map)
                return Response(content, mimetype='text/html')

        # Log this request in the 404 log and display not found page
        log_404(request)
        handler = get_view('not_found.main')
        content = handler(request)
        return Response(content, mimetype='text/html')
    except HTTPException, e:
        # TODO: log http exception so that I knew exactly what is going on with catonmat!
        print "HTTPException"
        pass
    finally:
        Session.remove()

application = SharedDataMiddleware(application,
    { '/static': path.join(path.dirname(__file__), 'static') }
)

