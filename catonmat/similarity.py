#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from catonmat.config            import config
from catonmat.cache             import cache
from catonmat.models            import Page, BlogPage, session, page_tags_table

from collections                import defaultdict

# ----------------------------------------------------------------------------

def jaccard_metric(s1, s2):
    return (len(s1.intersection(s2)) + 0.0)/len(s1.union(s2))


def simple_metric(s1, s2):
    return len(s1.intersection(s2))


def related_posts(post, n=10):
    posts_tags = get_posts_tags()
    this_post_tags = set(posts_tags[post.page_id])
    similarity = []
    for page_id in posts_tags:
        if page_id == post.page_id:
            continue
        score = jaccard_metric(this_post_tags, set(posts_tags[page_id]))
        similarity.append([page_id, score])
    top = sorted(similarity, key=lambda (page_id, score): score, reverse=True)
    for_in = []
    found = 0
    for page_id, score in top:
        if score == 0: break
        if session.query(BlogPage).filter_by(page_id=page_id).count() == 0:
            continue
        for_in.append(page_id)
        found = found + 1
        if found == n:
            break
    ret = []
    if for_in:
        pages = session.query(Page).join(BlogPage).filter(Page.page_id.in_(for_in)).all()
        d = dict([p.page_id, p] for p in pages)
        return [d[id] for id in for_in]
    return []


@cache('posts_tags')
def get_posts_tags():
    posts_tags = session.query(page_tags_table).all()
    ret = defaultdict(list)
    for page_id, tag_id in posts_tags:
        ret[page_id].append(tag_id)
    return ret

