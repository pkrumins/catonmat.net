#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from sqlalchemy                     import join

from werkzeug.exceptions            import NotFound

from catonmat.views.utils           import display_template_with_quote
from catonmat.models                import Tag, Page, UrlMap
from catonmat.database              import Session, page_tags_table

# ----------------------------------------------------------------------------

def main(request, tag):
    # TODO: perhaps this query is not necessary
    tag = Tag.query.filter_by(seo_name=tag).first()
    if not tag:
        raise NotFound()

    # TODO: more effective selection
    pus = Session.query(Page, UrlMap).join(
                (page_tags_table, Page.page_id==page_tags_table.c.page_id),
                (Tag, Tag.tag_id==page_tags_table.c.tag_id),
                UrlMap
          ).filter(Tag.tag_id==tag.tag_id).all()

    # TODO: add comment-count for each page, add excerpt, add publish date
    template_data = {
        'tag': tag,
        'pus': pus
    }
    return display_page('tag', template_data)


def list(request):
    tags = Tag.query.all()
    template_data = {
        'tags': tags
    }
    return display_page('tag_list', template_data)


def display_page(template, template_data):
    return display_template_with_quote(template, template_data)

