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
        if request.path[-1] == '/':
            request_path = request.path.rstrip('/');
            return redirect(request_path, code=301)

        url_map = find_url_map(request.path)
        if url_map:
            return handle_request('pages.main', request, url_map)

        # Log this request in the 404 log and display not found page
        if request.path not in [ "/wp-login.php", "/apple-touch-icon-precomposed.png", "/plus/mytag_js.php", "/apple-touch-icon-120x120-precomposed.png", "/apple-touch-icon-120x120.png", "/blog/wp-json/wp/v2/posts", "/blog/wp-json/wp/v2/users", "/ads.txt", "/plus/ad_js.php", "/apple-touch-icon-152x152-precomposed.png", "/apple-touch-icon-152x152.png", "/xmlrpc.php", "/utility/convert/data/config.inc.php", "/plus/download.php", "/config/AspCms_Config.asp", "/plus/mytag_j.php", "/plus/moon.php", "/data/img/css/xianf.ASP", "/bbs/utility/convert/data/config.inc.php", "/plus/bakup.hp", "/dxyylc/md5.aspx", "/plus/90sec.php", "/plus/laobiao.php", "/plus/e7xue.php", "/_s_/dyn/SessionState_ping", "/phpmyadmin", "/dxyylc/md5.php", "/browserconfig.xml", "/include/ckeditor/plugins/pagebreak/images/inCahe.php", "/include/code/mp.php", "/plus/mybak.php", "/install/m7lrv.php", "/weki.php", "/wordpress", "/wp", "/include/helperss/filter.helpear.php", "/templets/plus/sky.php", "/install/modurnlecscache.php", "/plus/xsvip.php", "/plus/myjs.php", "/include/data/fonts/uddatasql.php", "/plus/bakup.php", "/plus/av.php", "/data/cache/asd.php", "/lang/cn/system.php", "/data/data/index.php", "/sitemap/templates/met/SqlIn.asp", "/utility/convert/include/rom2823.php", "/xiaolei.php", "/data/conn/config.php", "/plus/mycak.php", "/plus/x.php", "/search.php", "/weki.asp", "/install/md5.php", "/Somnus/Somnus.asp", "/md5.asp", "/plus/read.php", "/plus/backup.php", "/plus/service.php", "/plus/spider.php", "/book/story_dod_hjkdsafon.php", "/plus/zdqd.php", "/data/s.asp", "/plus/90000.php" ]:
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

