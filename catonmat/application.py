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
from catonmat.views.utils import get_view
from catonmat.errorlog    import log_404, log_exception
from catonmat.urls        import predefined_urls, find_url_map, find_redirect
from catonmat.config      import config

from os import path

# ----------------------------------------------------------------------------

def handle_request(view, *values, **kw_values):
    handler = get_view(view)
    return handler(*values, **kw_values)


@Request.application
def application(request):
    try:
        adapter = predefined_urls.bind_to_environ(request.environ)
        endpoint, values = adapter.match()
        return handle_request(endpoint, request, **values)
    except NotFound:
        redir = find_redirect(request.path)
        if redir:
            return redirect(redir.new_path, code=redir.code)

        #print "Request path: " + request.path
        if request.path[-1] != '/':
            return redirect(request.path + '/', code=301)

        url_map = find_url_map(request.path)
        if url_map:
            return handle_request('pages.main', request, url_map)

        # Log this request in the 404 log and display not found page
        if request.path not in ["/wp-login.php/"]:
            log_404(request)
        return handle_request('not_found.main', request)
    except:
        log_exception(request)
        return handle_request('exception.main', request)
    finally:
        session.remove()

application = SharedDataMiddleware(application,
    { '/static': path.join(path.dirname(__file__), 'static') }
)

if config.use_profiler:
    from repoze.profile.profiler import AccumulatingProfileMiddleware
    application = AccumulatingProfileMiddleware(
                    application,
                    log_filename='/tmp/repoze-catonmat.txt',
                    cachegrind_filename='/tmp/repoze-catonmat-cachegrind',
                    discard_first_request=True,
                    flush_at_shutdown=True,
                    path='/__profile__'
                  )

