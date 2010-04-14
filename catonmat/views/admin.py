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

from catonmat.models                import session, Page, Revision, Category, UrlMap, Rss, BlogPage
from catonmat.views.utils           import display_template, render_template, template_response, MakoDict
from catonmat.admin                 import require_admin, REQUIRE_IP, logged_in, admin_cred_match_prim, hash_password, mk_secure_cookie
from catonmat.views.pages           import default_page_template_data, display_page

from datetime                       import datetime

import hashlib

# ----------------------------------------------------------------------------

@require_admin([REQUIRE_IP])
def index(request):
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
    if request.args.get('unpublished') is not None:
        all_pages = session.query(Page).filter_by(status='draft').order_by(Page.page_id).all()
    elif request.args.get('posts') is not None:
        all_pages = session.query(Page).filter_by(status='post').order_by(Page.page_id).all()
    elif request.args.get('pages') is not None:
        all_pages = session.query(Page).filter_by(status='page').order_by(Page.page_id).all()
    else:
        all_pages = session.query(Page).order_by(Page.page_id).all()
    return display_template('admin/pages', pages=all_pages)

@require_admin()
def edit_page(request, page_id):
    if request.method == "GET":
        page = session.query(Page).filter_by(page_id=page_id).first()
        cats = session.query(Category).all()
        return display_template('admin/edit_page', page=page, cats=cats)
    if 'submit' in request.form:
        return edit_page_submit(request, page_id)
    elif 'publish' in request.form:
        return publish_page(request, page_id)
    elif 'preview' in request.form:
        return edit_page_preview(request, page_id)

@require_admin()
def publish_page(request, page_id):
    page = session.query(Page).filter_by(page_id=page_id).first()
    if request.form['status'] == 'page':
        page.status = 'page'
        page.save()
    elif request.form['status'] == 'post':
        page.category.count = page.category.count + 1
        page.status = 'post'
        Rss(page, page.last_update).save()
        BlogPage(page, page.last_update).save()
        page.save()
    return redirect('/admin/edit_page/%d' % page.page_id)

@require_admin()
def edit_page_submit(request, page_id):
    page = session.query(Page).filter_by(page_id=page_id).first()
    cats = session.query(Category).all()

    page.title = request.form['title']
    page.content = request.form['content']
    page.excerpt = request.form['excerpt']
    page.last_update = datetime.utcnow()

    if page.category.category_id != int(request.form['cat_id']):
        update_category(page, request.form['cat_id'])

    if request.form['request_path']:
        if page.url_map:
            page.url_map.request_path = request.form['request_path']
        else:
            urlmap = UrlMap(request.form['request_path'], page.page_id).save()
            page.urlmap = urlmap
    else:
        if page.url_map:
            session.delete(page.url_map)

    page.save()

    change_note = request.form['change_note'].strip()
    if change_note:
        Revision(page, change_note).save()
    return display_template('admin/edit_page', page=page, cats=cats)

def update_category(page, new_cat_id):
    if page.status == 'draft':
        page.category_id = new_cat_id
        return

    # update page category count only if page is published
    old_cat = page.category
    new_cat = session.query(Category).filter_by(category_id=new_cat_id).first()

    old_cat.count = old_cat.count - 1
    new_cat.count = new_cat.count + 1

    page.category = new_cat

@require_admin()
def edit_page_preview(request, page_id):
    session.autoflush = False
    page = session.query(Page).autoflush(False).filter_by(page_id=page_id).first()
    page.title = request.form['title']
    page.content = request.form['content']
    page.excerpt = request.form['excerpt']
    page.category_id = request.form['cat_id']

    # TODO: merge with views/pages.py
    map = MakoDict(dict(page=page, request_path=page.request_path))
    return display_page(default_page_template_data(request, map))

@require_admin()
def new_page(request):
    if request.method == "GET":
        cats = session.query(Category).all()
        return display_template('admin/new_page', cats=cats)
    if 'submit' in request.form:
        page = new_page_from_request(request)
        return redirect('/admin/edit_page/%d' % page.page_id)

def new_page_from_request(request):
    page = Page(
             request.form['title'],
             request.form['content'],
             request.form['excerpt'],
             category_id=request.form['cat_id'])
    page.status = 'draft'
    page.save()

    if request.form['request_path']:
        urlmap = UrlMap(request.form['request_path'], page.page_id).save()
        page.urlmap = urlmap
        page.save()

    return page

@require_admin()
def cats(request):
    cats = session.query(Category).all()
    return display_template('admin/cats', cats=cats)

