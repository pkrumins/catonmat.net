#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# This program imports a wordpress database into the new catonmat database
#
# Code is licensed under GNU GPL license.
#

import sys
sys.path.append('/home/pkrumins/catonmat')

from sqlalchemy         import MetaData, create_engine
from sqlalchemy         import Table
from sqlalchemy.orm     import sessionmaker

from catonmat.models    import (
    Page, Tag, Category, Comment, Visitor, UrlMap, BlogPage, Rss, Download
)

from mimetypes          import guess_type
from collections        import defaultdict
from urlparse           import urlparse

import re

# ----------------------------------------------------------------------------

engine = create_engine('mysql://root@localhost/catonmat_wordpress?charset=utf8')
metadata = MetaData(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

wp_pages_table = Table('wp_posts', metadata, autoload=True)
wp_tags_table = Table('wp_tags', metadata, autoload=True)
wp_post2tag_table = Table('wp_post2tag', metadata, autoload=True)
wp_comments_table = Table('wp_comments', metadata, autoload=True)
wp_categories_table = Table('wp_categories', metadata, autoload=True)
wp_post2cat_table = Table('wp_post2cat', metadata, autoload=True)
wp_downloads_table = Table('wp_DLM_DOWNLOADS', metadata, autoload=True)

def enumerate1(iterable):
    for a, b in enumerate(iterable):
        yield a+1, b

def flush_write(str):
    sys.stdout.write(str)
    sys.stdout.flush()

def wordpress_to_catonmat():
    wp_pages = get_wp_pages()
    wp_tags_dict = get_wp_tags()
    wp_comments_dict = get_wp_comments()
    wp_categories_dict = get_wp_categories()
    wp_downloads = get_wp_downloads()

    import_categories(wp_categories_dict)
    import_downloads(wp_downloads)
    import_pages(wp_pages, wp_tags_dict, wp_comments_dict, wp_categories_dict)

def import_downloads(wp_downloads):
    def get_mimetype(filename):
        plaintext_mimes = "awk php phps vb vbs pl pm perl conf py python c cpp".split()
        try:
            ext = filename.split('.')[1]
            if ext in plaintext_mimes:
                return 'text/plain'
        except (IndexError, KeyError):
            pass
        return guess_type(filename)[0]

    flush_write("Importing downloads. ")
    for wp_download in wp_downloads:
        filename = re.sub(r'.*/', '', wp_download.filename)
        mimetype = get_mimetype(filename)
        cm_download = Download(wp_download.title, filename, \
                        mimetype, wp_download.hits, wp_download.postDate)
        cm_download.save()
    flush_write("Done.\n")

def import_categories(wp_categories_dict):
    flush_write("Importing categories. ")
    for wp_cat in wp_categories_dict.values():
        cm_cat = Category(wp_cat.cat_name, wp_cat.category_nicename, wp_cat.category_description)
        wp_cat.cm_cat = cm_cat
        cm_cat.save()
    flush_write("Done.\n")

def import_pages(wp_pages, wp_tags_dict, wp_comments_dict, wp_categories_dict):
    def print_status(npk):
        if npk % 10 == 0: flush_write("(%d)" % npk)
        else:             flush_write('.')

    flush_write("Importing pages, comments, tags, urlmaps, blogpages and rss.\n")
    for npk, wp_page in enumerate1(wp_pages):
        print_status(npk)

        cm_page = Page(wp_page.post_title, wp_page.post_content, wp_page.post_excerpt, 
                       wp_page.post_date, wp_page.post_modified)
        import_page_tags(wp_page, cm_page, wp_tags_dict)
        import_page_category(wp_page, cm_page, wp_categories_dict)
        cm_page.save() # to generate cm_page.page_id
        import_page_comments(wp_page, cm_page.page_id, wp_comments_dict)
        generate_urlmap(wp_page, cm_page.page_id)
        insert_blogpage(wp_page, cm_page)
        insert_rss(wp_page, cm_page)
    flush_write("Done.\n")

def import_page_tags(wp_page, cm_page, wp_tags_dict):
    wp_tags = get_page_tags(wp_page, wp_tags_dict)
    for wp_tag in wp_tags:
        tag_seo_name = wp_tag
        tag_name = wp_tag.replace('-', ' ')
        cm_page.add_tag(Tag(tag_name, tag_seo_name))

def import_page_category(wp_page, cm_page, wp_categories_dict):
    wp_cat = get_page_category(wp_page)
    cm_page.category = wp_categories_dict[wp_cat].cm_cat
    if wp_page.post_type == 'post' and wp_page.post_status == 'publish':
        cm_page.category.count += 1

def import_page_comments(wp_page, cm_page_id, wp_comments_dict):
    for comment in wp_comments_dict[wp_page.ID]:
        visitor = Visitor(comment.comment_author_IP, timestamp=comment.comment_date)
        Comment(cm_page_id, comment.comment_author,
                comment.comment_content,
                visitor,
                email=comment.comment_author_email,
                website=comment.comment_author_url,
                timestamp=comment.comment_date).save()

def generate_urlmap(wp_page, cm_page_id):
    parsed = urlparse(wp_page.guid)
    path = parsed.path.rstrip('/')
    if path:
        UrlMap(parsed.path.rstrip('/'), cm_page_id).save()
    elif wp_page.ID==2: # 2nd post for some reason doesn't have a path in my db
        UrlMap('/about', cm_page_id).save()
    
def insert_blogpage(wp_page, cm_page):
    if wp_page.post_type == 'post' and wp_page.post_status == 'publish':
        BlogPage(cm_page, cm_page.created).save()

def insert_rss(wp_page, cm_page):
    if wp_page.post_type == 'post' and wp_page.post_status == 'publish':
        Rss(cm_page, cm_page.created).save()

def get_wp_pages():
    flush_write("Getting wordpress pages. ")
    pages = session. \
              query(wp_pages_table). \
              filter(wp_pages_table.c.post_type.in_(['page', 'post'])). \
              order_by(wp_pages_table.c.ID.asc()). \
              all()
    flush_write("Got %d wordpress pages.\n" % len(pages))
    return pages

def get_wp_tags():
    flush_write("Getting wordpress tags. ")
    all_tags = session.query(wp_tags_table).all()
    wp_tags_dict = dict([t.tag_ID, t.tag] for t in all_tags)
    flush_write("Got %d wordpress tags.\n" % len(wp_tags_dict))
    return wp_tags_dict

def get_wp_comments():
    flush_write("Getting wordpress comments. ")
    all_comments = session.query(wp_comments_table). \
                     filter(wp_comments_table.c.comment_type==''). \
                     filter(wp_comments_table.c.comment_approved=='1'). \
                     order_by(wp_comments_table.c.comment_ID.asc()). \
                     all()
    wp_comments_dict = defaultdict(list)
    for comment in all_comments:
        wp_comments_dict[comment.comment_post_ID].append(comment)
    flush_write("Got %d wordpress comments.\n" % len(all_comments))
    return wp_comments_dict

def get_wp_categories():
    flush_write("Getting wordpress categories. ")
    all_categories = session.query(wp_categories_table). \
                       filter(wp_categories_table.c.category_count>0). \
                       all()
    wp_cat_dict = dict([c.cat_ID, c] for c in all_categories)
    flush_write("Got %d wordpress categories.\n" % len(wp_cat_dict))
    return wp_cat_dict

def get_wp_downloads():
    flush_write("Getting wordpress downloads. ")
    wp_downloads = session.query(wp_downloads_table). \
                    order_by(wp_downloads_table.c.id).all()
    flush_write("Got %d wordpress downloads.\n" % len(wp_downloads))
    return wp_downloads

def get_page_tags(page, wp_tags):
    tags = session. \
             query(wp_post2tag_table). \
             filter(wp_post2tag_table.c.post_id==page.ID). \
             all()
    ids = [tag.tag_id for tag in tags]
    return [wp_tags[id] for id in ids]

def get_page_category(page):
    cats = session. \
             query(wp_post2cat_table). \
             filter(wp_post2cat_table.c.post_id==page.ID). \
             first()
    return cats.category_id

if __name__ == "__main__":
    wordpress_to_catonmat()

