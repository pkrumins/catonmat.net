#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug                       import Response, redirect
from werkzeug.contrib.atom          import AtomFeed

from catonmat.config                import config
from catonmat.cache                 import cache
from catonmat.database              import session
from catonmat.models                import Page, Rss

import re

# ----------------------------------------------------------------------------

feedburner_re = re.compile(r'feedburner|feedvalidator', re.I)

def feedburner_bot(request):
    ua = request.headers.get('User-Agent')
    if ua and feedburner_re.search(ua):
        return True
    return False

def atom_feed(request):
    if feedburner_bot(request):
        feed = compute_atom_feed(request)
        return Response(feed, mimetype='application/atom+xml')
    return redirect('http://feeds.feedburner.com/catonmat', code=302)

peteris = {
    'name':  'Peteris Krumins',
    'uri':   'http://www.catonmat.net/about',
    'email': 'peter@catonmat.net'
}

catonmat_title    = "good coders code, great reuse"
catonmat_subtitle = "Peteris Krumins' blog about programming, hacking, software reuse, software ideas, computer security, google and technology."

@cache('atom_feed')
def compute_atom_feed(request):
    feed = AtomFeed(
             title     = catonmat_title,
             subtitle  = catonmat_subtitle,
             feed_url  = 'http://www.catonmat.net/feed',
             url       = 'http://www.catonmat.net',
             author    = peteris,
             icon      = 'http://www.catonmat.net/favicon.ico',
             generator = ('catonmat blog', 'http://www.catonmat.net', 'v1.0')
           )

             # TODO: logo='http://www.catonmat.net/)

    pages = session. \
              query(Page). \
              join(Rss). \
              order_by(Rss.publish_date.desc()). \
              limit(config.rss_items). \
              all()

    for page in pages:
        feed.add(title        = page.title,
                 content      = page.parsed_content,
                 content_type = 'html',
                 author       = peteris,
                 url          = 'http://www.catonmat.net' + page.request_path,
                 id           = page.page_id,
                 updated      = page.last_update,
                 published    = page.rss_page.publish_date)

    return feed.to_string()

