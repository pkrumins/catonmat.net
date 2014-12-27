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

    if request.args.get('type') == 'unpublished':
        query = query.filter_by(status='draft')
    elif request.args.get('type') == 'posts':
        query = query.filter_by(status='post')
    elif request.args.get('type') == 'pages':
        query = query.filter_by(status='page')

    if request.args.get('sort') == 'id_desc' or request.args.get('sort') is None:
        query = query.order_by(Page.page_id.desc())
    elif request.args.get('sort') == 'id_asc':
        query = query.order_by(Page.page_id.asc())
    elif request.args.get('sort') == 'created_asc':
        query = query.order_by(Page.created.asc())
    elif request.args.get('sort') == 'created_desc':
        query = query.order_by(Page.created.desc())

    all_pages = query.order_by(Page.page_id).all()
    return display_plain_template('admin/pages', pages=all_pages)

