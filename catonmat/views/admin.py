#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug                       import redirect

from catonmat.models                import Page, session
from catonmat.views.utils           import display_template, render_template, template_response
from catonmat.admin                 import require_admin, REQUIRE_IP, logged_in, admin_cred_match_prim, hash_password, mk_secure_cookie

import hashlib

# ----------------------------------------------------------------------------

@require_admin([REQUIRE_IP])
def index(request):
    print request.cookies
    if not logged_in(request):
        return display_template('admin/login')
    return display_template('admin/index')

@require_admin([REQUIRE_IP])
def login(request):
    if request.method != "POST":
        return display_template('admin/login', message="Not a POST request")
    
    user = request.form.get('a')
    hash = hash_password(request.form.get('b'))
    if admin_cred_match_prim(user, hash):
        cookie = {
            'admin_user': user,
            'admin_hash': hash
        }
        response = redirect('/admin')
        response.set_cookie('admin', mk_secure_cookie(cookie).serialize(), httponly=True)
        return response

    return display_template('admin/login', message="Password incorrect")

@require_admin()
def pages(request):
    all_pages = session.query(Page).order_by(Page.page_id).all()
    return display_template('admin/pages', pages=all_pages)

@require_admin()
def edit_page(request, page_id):
    if request.method == "GET":
        page = session.query(Page).filter_by(page_id=page_id).first()
        return display_template('admin/edit_page', page=page)
    return edit_page_submit(request, page_id)

def edit_page_submit(request, page_id):
    page = session.query(Page).filter_by(page_id=page_id).first()
    page.title = request.form['title']
    page.content = request.form['content']
    page.save()
    return display_template('admin/edit_page', page=page)

