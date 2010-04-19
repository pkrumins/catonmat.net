#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from catonmat.models            import session, Page
from catonmat.admin             import require_admin
from catonmat.views.utils       import display_plain_template

# ----------------------------------------------------------------------------

@require_admin()
def main(request):
    query = session.query(Page)

    if request.args.get('unpublished') is not None:
        query = query.filter_by(status='draft')
    elif request.args.get('posts') is not None:
        query = query.filter_by(status='post')
    elif request.args.get('pages') is not None:
        query = query.filter_by(status='page')

    all_pages = query.order_by(Page.page_id).all()
    return display_plain_template('admin/pages', pages=all_pages)

