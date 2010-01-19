#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# Code is licensed under MIT license.
#

from catonmat.models  import UrlMap
from werkzeug.routing import Map, Rule as RuleBase, Submount

import re

# ----------------------------------------------------------------------------

def get_page_from_request_path(request_path):
    request_path = request_path.rstrip('/')
    request_path = re.sub('//+', '/', request_path)

    return UrlMap.query.filter_by(request_path=request_path).first()


class Rule(RuleBase):
    def __gt__(self, endpoint):
        self.endpoint = endpoint
        return self


url_map = Map([
    Rule('/')                         > 'index.main',
    Rule('/blog')                     > 'index.main',
    Rule('/quotes')                   > 'quotes.main',
    Rule('/download/<file>')          > 'downloads.main',

    Rule('/_service/comment_preview') > 'catonmat.comments.preview_comment',

    # This is currently unnecessary
    Rule('/_service/comment_add')     > 'catonmat.comments.add_comment',

    # Short URL for comments
    Rule('/c/<int:id>')               > 'pages.comment',

    # Short URL for pages
    Rule('/p/<int:id>')               > 'pages.shorturl'
])

