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

from catonmat.models            import session, Page, Category, Revision, Tag, Rss, BlogPage
from catonmat.admin             import require_admin
from catonmat.views.utils       import display_plain_template, MakoDict
from catonmat.views.pages       import default_page_template_data, display_page
from catonmat.cache             import cache_del
from catonmat.config            import config

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
    if config.use_cache:
        cache_del('posts_tags')
        if page.request_path:
            cache_del('individual_page_%s' % page.request_path)

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
    status = request.form['status']

    if status == 'page':
        page.status = 'page'
        page.save()
    elif status == 'post':
        page.category.count = Category.count + 1
        page.status = 'post'
        publish_date = datetime.strptime(request.form['publish_date'], '%Y-%m-%d %H:%M:%S')
        Rss(page, publish_date).save()
        BlogPage(page, publish_date).save()
        page.save()

    if status == 'page' or status == 'post':
        if config.use_cache:
            cache_del('individual_page_%s' % page.request_path)
            cache_del('page_list')
            cache_del('index_page_1')
            cache_del('posts_tags')
            if status == 'post':
                cache_del('atom_feed')
            # TODO: optimize cache invalidation method, and invalidate tags and categories

        draft_tags = page.get_meta('draft_tags')
        if draft_tags:
            tags = tag_list(draft_tags)
            for tag in tags:
                seo_name = tag.replace(' ', '-')
                page.add_tag(Tag(tag, seo_name))
        page.delete_meta('draft_tags')

    return redirect('/admin/edit_page/%d' % page.page_id)

