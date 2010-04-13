#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under MIT license.
#

from catonmat.cache         import from_cache_or_compute
from catonmat.models        import UrlMap, Redirect
from catonmat.database      import session

from werkzeug.routing       import Map, Rule as RuleBase, Submount

import re

# ----------------------------------------------------------------------------

def agreed_path(request_path):
    request_path = request_path.rstrip('/')
    request_path = re.sub('//+', '/', request_path)
    return request_path


def find_redirect(request_path):
    request_path = agreed_path(request_path)
    cache_key = 'redirect_%s' % request_path
    return from_cache_or_compute(find_redirect_compute, cache_key, 0, request_path)


def find_redirect_compute(request_path):
    return session.query(Redirect).filter_by(old_path=request_path).first()


def find_url_map(request_path):
    request_path = agreed_path(request_path)
    cache_key = 'not_found_%s' % request_path
    return from_cache_or_compute(find_url_map_compute, cache_key, 0, request_path)


def find_url_map_compute(request_path):
    return session.query(UrlMap).filter_by(request_path=request_path).first()


class Rule(RuleBase):
    def __gt__(self, endpoint):
        self.endpoint = endpoint
        return self


predefined_urls = Map([
    # Main page
    Rule('/')                          > 'index.main',

    # Pagination
    Rule('/page')                      > 'index.page_list',
    Rule('/pages')                     > 'index.page_list',
    Rule('/page/<int:page_nr>')        > 'index.page',

    # Search
    Rule('/search')                    > 'search.main',

    # Atom feed
    Rule('/feed')                      > 'rss.atom_feed',
    Rule('/feed/atom')                 > 'rss.atom_feed',
    Rule('/feed/rss')                  > 'rss.atom_feed',

    # Blog is alias for Main page right now
    Rule('/blog')                      > 'index.main',

    # Feedback
    Rule('/feedback')                  > 'feedback.main',

    # Sitemap
    Rule('/sitemap')                   > 'sitemap.main',

    # Article Series
    Rule('/series')                    > 'series.main',
    Rule('/series/<seo_name>')         > 'series.single',

    # Categories
    Rule('/category/<seo_name>')       > 'categories.main',
    Rule('/category')                  > 'categories.list',
    Rule('/categories')                > 'categories.list',

    # Tags
    Rule('/tag/<seo_name>')            > 'tags.main',
    Rule('/tag')                       > 'tags.list',
    Rule('/tags')                      > 'tags.list',

    # Article archive
    Rule('/archive')                        > 'archive.main',
    Rule('/archive/<int:year>')             > 'archive.year',
    Rule('/archive/<int:year>/<int:month>') > 'archive.year_month',

    # Programming quotes
    Rule('/quotes')                    > 'quotes.main',

    # Downloads
    Rule('/download/<filename>')       > 'downloads.main',
    Rule('/blog/wp-content/plugins/wp-downloadMonitor/user_uploads/<filename>') > 'downloads.old_wp_download',
    Rule('/wp-content/plugins/wp-downloadMonitor/user_uploads/<filename>') > 'downloads.old_wp_download',

    # Add and preview comments via AJAX
    Rule('/_services/comment_preview') > 'catonmat.comments.preview_comment',
    Rule('/_services/comment_add')     > 'catonmat.comments.add_comment',

    # Short URL for comments
    Rule('/c/<int:comment_id>')        > 'c.main',

    # Short URL for pages
    Rule('/p/<int:page_id>')           > 'p.main',

    # News
    Rule('/news')                      > 'news.main',

    # Admin
    Submount('/admin', [
        Rule('/')                      > 'admin.index',
        Rule('/login')                 > 'admin.login',
        Rule('/pages')                 > 'admin.pages',
        Rule('/edit_page/<page_id>')   > 'admin.edit_page',
        Rule('/cats')                  > 'admin.cats'
    ])
],
strict_slashes=False)

