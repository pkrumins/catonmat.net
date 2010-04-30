#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug.exceptions        import NotFound

from catonmat.models            import (
    Page, ArticleSeries, Comment, Tag, Category, SearchHistory, session
)
from catonmat.search            import search, SearchError
from catonmat.views.utils       import display_template, MakoDict
from catonmat.errorlog          import log_exception

# ----------------------------------------------------------------------------

def main(request):
    query = request.args.get('q')
    if not query:
        # TODO: display latest/top search queries instead of raising NotFound
        return display_template('search_empty')

    SearchHistory(query, request).save()

    try:
        page_results    = search(query, 'pages')
        as_results      = search(query, 'article_series')
        comment_results = search(query, 'comments')
        tag_results     = search(query, 'tags')
        cat_results     = search(query, 'categories')
    except SearchError, e:
        log_exception(request)
        return display_template('search_failed', query=query, error=e.message)

    pages    = get_pages(page_results)
    article_series = get_as(as_results)
    comments = get_comments(comment_results)
    tags     = get_tags(tag_results)
    cats     = get_cats(cat_results)

    return display_template('search',
             query=query,
             page_results=MakoDict(page_results),
             pages=pages,
             as_results=MakoDict(as_results),
             article_series=article_series,
             comment_results=MakoDict(comment_results),
             comments=comments,
             tag_results=MakoDict(tag_results),
             tags=tags,
             cat_results=MakoDict(cat_results),
             cats=cats)


# TODO: abstract this code.
def get_pages(page_results):
    page_ids = extract_ids(page_results['matches'])
    if not page_ids:
        return []
    pages = session. \
              query(Page). \
              filter(Page.page_id.in_(page_ids)). \
              all()
    d = dict([p.page_id, p] for p in pages)
    return [d[id] for id in page_ids]


def get_as(as_results):
    as_ids = extract_ids(as_results['matches'])
    if not as_ids:
        return []
    article_series = session. \
                       query(ArticleSeries). \
                       filter(ArticleSeries.series_id.in_(as_ids)). \
                       all()
    d = dict([a.series_id, a] for a in article_series)
    return [d[id] for id in as_ids]


def get_comments(comment_results):
    comment_ids = extract_ids(comment_results['matches'])
    if not comment_ids:
        return []
    comments = session. \
                 query(Comment). \
                 filter(Comment.comment_id.in_(comment_ids)). \
                 all()
    d = dict([c.comment_id, c] for c in comments)
    return [d[id] for id in comment_ids]


def get_tags(tag_results):
    tag_ids = extract_ids(tag_results['matches'])
    if not tag_ids:
        return []
    tags = session. \
             query(Tag). \
             filter(Tag.tag_id.in_(tag_ids)). \
             all()
    d = dict([t.tag_id, t] for t in tags)
    return [d[id] for id in tag_ids]


def get_cats(cat_results):
    cat_ids = extract_ids(cat_results['matches'])
    if not cat_ids:
        return []
    cats = session. \
             query(Category). \
             filter(Category.category_id.in_(cat_ids)). \
             all()
    d = dict([c.category_id, c] for c in cats)
    return [d[id] for id in cat_ids]


def extract_ids(matches):
    return [m['id'] for m in matches]

