#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug.exceptions            import NotFound

from catonmat.models                import Tag, Page, UrlMap
from catonmat.database              import page_tags_table, session
from catonmat.views.utils           import cached_template_response, render_template

# ----------------------------------------------------------------------------

def main(request, seo_name):
    return cached_template_response(
             'tag_page_%s' % seo_name,
             compute_main,
             request,
             seo_name)


def compute_main(request, seo_name):
    # TODO: perhaps this query is not necessary
    tag = session.query(Tag).filter_by(seo_name=seo_name).first()
    if not tag:
        raise NotFound()

    # TODO: more effective selection
    pus = session.query(Page, UrlMap).join(
                (page_tags_table, Page.page_id==page_tags_table.c.page_id),
                (Tag, Tag.tag_id==page_tags_table.c.tag_id),
                UrlMap
          ).filter(Tag.tag_id==tag.tag_id).all()

    # TODO: add comment-count for each page, add excerpt, add publish date
    template_data = {
        'tag': tag,
        'pus': pus
    }
    return render_template('tag', **template_data)


def list(request):
    return cached_template_response(
             'tag_list',
             compute_list,
             request)


def compute_list(request):
    tags = session.query(Tag).order_by(Tag.name).all()
    template_data = {
        'tags': tags
    }
    return render_template('tag_list', **template_data)

