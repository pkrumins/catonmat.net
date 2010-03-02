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
    # Main page
    Rule('/')                          > 'index.main',

    # Pagination
    Rule('/page/<int:page_nr>')        > 'index.page',

    # Blog is alias for Main page right now
    Rule('/blog')                      > 'index.main',

    # Categories
    Rule('/category/<category>')       > 'categories.main',
    Rule('/category')                  > 'categories.list',
    Rule('/categories')                > 'categories.list',

    # Tags
    Rule('/tag/<tag>')                 > 'tags.main',
    Rule('/tag')                       > 'tags.list',
    Rule('/tags')                      > 'tags.list',

    # Programming quotes
    Rule('/quotes')                    > 'quotes.main',

    # Downloads
    Rule('/download/<file>')           > 'downloads.main',

    # Add and preview comments via AJAX
    Rule('/_services/comment_preview') > 'catonmat.comments.preview_comment',
    Rule('/_services/comment_add')     > 'catonmat.comments.add_comment',

    # Short URL for comments
    Rule('/c/<int:comment_id>')        > 'c.main',

    # Short URL for pages
    Rule('/p/<int:page_id>')           > 'p.main'
])

