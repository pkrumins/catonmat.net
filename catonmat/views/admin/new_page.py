#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug                   import redirect

from catonmat.models            import session, Page, Category
from catonmat.admin             import require_admin
from catonmat.views.utils       import display_plain_template

# ----------------------------------------------------------------------------

@require_admin()
def main(request):
    if request.method == "GET":
        cats = session.query(Category).all()
        return display_plain_template('admin/new_page', cats=cats)
    if 'submit' in request.form:
        page = new_page(request)
        return redirect('/admin/edit_page/%d' % page.page_id)


def new_page(request):
    page = Page(
             request.form['title'],
             request.form['content'],
             request.form['excerpt'],
             category_id=request.form['cat_id'])
    page.status = 'draft'
    page.request_path = request.form['request_path']

    draft_tags = request.form['tags'].strip()
    if draft_tags:
        page.set_meta('draft_tags', draft_tags)

    page.save()

    return page

