#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# Code is licensed under MIT license.
#

from catonmat.config        import config
from catonmat.cache         import cache_get, cache_set
from catonmat.models        import UrlMap
from catonmat.database      import session

from werkzeug.routing       import Map, Rule as RuleBase, Submount

import re

# ----------------------------------------------------------------------------

def url_map_for_path(request_path):
    cache_key = 'not_found_%s' % request_path

    request_path = request_path.rstrip('/')
    request_path = re.sub('//+', '/', request_path)

    if config.use_cache:
        url_map = cache_get(cache_key)
        if url_map is not None:
            return url_map

    url_map = session.query(UrlMap).filter_by(request_path=request_path).first()
    if not url_map:
        return None

    if config.use_cache:
        cache_set(cache_key, url_map)

    return url_map


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
    Rule('/category/<seo_name>')       > 'categories.main',
    Rule('/category')                  > 'categories.list',
    Rule('/categories')                > 'categories.list',

    # Tags
    Rule('/tag/<seo_name>')            > 'tags.main',
    Rule('/tag')                       > 'tags.list',
    Rule('/tags')                      > 'tags.list',

    # Programming quotes
    Rule('/quotes')                    > 'quotes.main',

    # Downloads
    Rule('/download/<filename>')       > 'downloads.main',

    # Add and preview comments via AJAX
    Rule('/_services/comment_preview') > 'catonmat.comments.preview_comment',
    Rule('/_services/comment_add')     > 'catonmat.comments.add_comment',

    # Short URL for comments
    Rule('/c/<int:comment_id>')        > 'c.main',

    # Short URL for pages
    Rule('/p/<int:page_id>')           > 'p.main'
])

