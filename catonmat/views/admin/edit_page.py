#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from catonmat.models            import session, Page, Category, Revision, Tag
from catonmat.admin             import require_admin
from catonmat.views.utils       import display_plain_template, MakoDict
from catonmat.views.pages       import default_page_template_data, display_page

from datetime                   import datetime

# ----------------------------------------------------------------------------

@require_admin()
def main(request, page_id):
    if request.method == "GET":
        page = session.query(Page).filter_by(page_id=page_id).first()
        cats = session.query(Category).all()
        return display_plain_template('admin/edit_page', page=page, cats=cats)

    if 'submit' in request.form:
        return edit_page_submit(request, page_id)
    elif 'publish' in request.form:
        return publish_page(request, page_id)
    elif 'preview' in request.form:
        return edit_page_preview(request, page_id)


def edit_page_submit(request, page_id):
    page = session.query(Page).filter_by(page_id=page_id).first()
    page_cat = session.query(Category).filter_by(category_id=request.form['cat_id']).first()

    page.title        = request.form['title']
    page.content      = request.form['content']
    page.excerpt      = request.form['excerpt']
    page.request_path = request.form['request_path']
    page.category     = page_cat
    page.last_update  = datetime.utcnow()

    if page.status == 'draft':
        page.set_meta('draft_tags', request.form['tags'])
    else:
        new_tags = set(tag_list(request.form['tags']))
        old_tags = set([t.name for t in page.tags])

        removed_tags = old_tags-new_tags
        if removed_tags:
            for tag in removed_tags:
                page.delete_tag(tag)

        new_tags = new_tags-old_tags
        if new_tags:
            for tag in new_tags:
                seo_name = tag.replace(' ', '-')
                page.add_tag(Tag(tag, seo_name))

    page.save()

    change_note = request.form['change_note'].strip()
    if change_note:
        Revision(page, change_note).save()

    cats = session.query(Category).all()
    return display_plain_template('admin/edit_page', page=page, cats=cats)


def tag_list(tag_str):
    if not tag_str:
        return []
    return [t.strip() for t in tag_str.split(',')]


def edit_page_preview(request, page_id):
    session.autoflush = False

    page = session.query(Page).filter_by(page_id=page_id).first()
    page_cat = session.query(Category).filter_by(category_id=request.form['cat_id']).first()

    page.title = request.form['title']
    page.content = request.form['content']
    page.excerpt = request.form['excerpt']
    page.category = page_cat

    map = MakoDict({
            'page':         page,
            'request_path': page.request_path
    })
    return display_page(default_page_template_data(request, map))


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

