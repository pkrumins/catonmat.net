#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from sqlalchemy.orm         import dynamic_loader, relation

from catonmat.database      import (
    pages_table,     revisions_table, urlmaps_table,    fourofour_table,
    blogpages_table, comments_table,  categories_table, tags_table,
    page_tags_table,
    mapper
)

from urlparse               import urlparse
from datetime               import datetime

import hashlib

# ----------------------------------------------------------------------------

class Page(object):
    def __init__(self, title, content=None, excerpt=None, created=None, last_update=None, category_d=None):
        self.title = title
        self.content = content
        self.excerpt = excerpt
        self.created = created
        self.last_update = last_update
        self.category_id = category_id
        
        if self.created is None:
            self.created = datetime.utcnow()
        if self.last_update is None:
            self.last_update = datetime.utcnow()

    @property
    def parsed_content(self):
        return parse_page(self.content)

    @property
    def publish_time(self):
        return self.created.strftime("%B %d, %Y")

    @property
    def comment_count(self):
        return Comment.query.filter_by(page_id=self.page_id).count()

    def __repr__(self):
        return '<Page: %s>' % self.title


class Comment(object):
    def __init__(self, page_id, name, comment, parent_id=None, email=None, twitter=None, website=None, timestamp=None):
        self.page_id = page_id
        self.parent_id = parent_id
        self.name = name
        self.comment = comment
        self.email = email
        self.gravatar_md5 = ""
        self.twitter = twitter
        self.website = website

        if website:
            url = urlparse(website)
            if not url.scheme:
                self.website = 'http://' + website

        if parent_id == '':
            self.parent_id = None
        if email:
            self.gravatar_md5 = hashlib.md5(email).hexdigest()
        if timestamp is None:
            self.timestamp = datetime.utcnow()

    @property
    def parsed_comment(self):
        return parse_comment(self.comment)

    @property
    def publish_time(self):
        return self.timestamp.strftime("%B %d, %Y, %H:%M")

    def __repr__(self):
        return '<Comment(%d) on Page(%s)>' % (self.comment_id, self.page.title)


class Revision(object):
    def __init__(self, page, change_note, timestamp=None):
        self.page = page
        self.change_note = change_note
        self.timestamp = timestamp

        self.title = page.title
        self.content = page.content
        self.excerpt = page.excerpt

        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def __repr__(self):
        return '<Revision of Page(%s)>' % self.page.title


class Category(object):
    def __init__(self, name, seo_name, description, count=0):
        self.name = name
        self.seo_name = seo_name
        self.description = description
        self.count = count

    def __repr__(self):
        return '<Category %s>' % self.name


class Tag(object):
    def __init__(self, name, seo_name, description, count=0):
        self.name = name
        self.seo_name = seo_name
        self.description = description
        self.count = count

    def __repr__(self):
        return '<Tag %s>' % self.name


class UrlMap(object):
    def __init__(self, request_path, page, handler=None):
        self.request_path = request_path
        self.page_id = page.page_id
        self.handler = handler

    def __repr__(self):
        return '<UrlMap from %s to Page(%s)>' % (self.request_path, self.page.title)


class FouroFour(object):
    def __init__(self, request_path, date=None):
        self.request_path = request_path
        if self.date is None:
            self.date = datetime.utcnow()

    def __repr__(self):
        return '<404 of %s>' % (self.request_path)


class BlogPages(object):
    def __init__(self, page, publish_date=None, visible=True):
        self.page = page
        self.page_id = page.page_id
        self.visible = visible

        if publish_date is None:
            self.publish_date = date.utcnow()

    def __repr__(self):
        return '<Blog Page of Page(%s)>' % page.title


mapper(Page, pages_table, properties={
    'revisions': dynamic_loader(
                    Revision,
                    backref='page',
                    order_by=revisions_table.c.revision_id.desc()
    ),
    'comments': dynamic_loader(
                    Comment,
                    backref='page',
                    order_by=comments_table.c.comment_id.asc()
    ),
    'category': relation(Category),
    'tags':     relation(
                    Tag,
                    secondary=page_tags_table,
                    order_by=tags_table.c.name
    )
})
mapper(Comment,  comments_table)
mapper(Revision, revisions_table)
mapper(Category, categories_table)
mapper(Tag,      tags_table, properties={
    'pages': dynamic_loader(Page, secondary=page_tags_table)
})
mapper(UrlMap, urlmaps_table, properties={
    'page': relation(Page)
})
mapper(FouroFour, fourofour_table)
mapper(BlogPages, blogpages_table, properties={
    'page': relation(Page)
})

# Cyclic references
from catonmat.parser    import parse_page, parse_comment

