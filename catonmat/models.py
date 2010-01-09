#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website. See this post for more info:
# http://www.catonmat.net/blog/50-ideas-for-the-new-catonmat-website/
#
# Code is licensed under GNU GPL license.
#

from datetime import datetime
from sqlalchemy.orm import dynamic_loader, relation
from catonmat.database import (
    pages_table,     revisions_table, urlmaps_table, fourofour_table,
    blogpages_table, comments_table
)
from catonmat.database import mapper

class Page(object):
    def __init__(self, title, content=None, excerpt=None, created=None, last_update=None):
        self.title = title
        self.content = content
        self.excerpt = excerpt
        self.created = created
        self.last_update = last_update
        
        if self.created is None:
            self.created = datetime.utcnow()
        if self.last_update is None:
            self.last_update = datetime.utcnow()

    def __repr__(self):
        return '<Page: %s>' % self.title

class Comment(object):
    def __init__(self, page_id, name, comment, email=None, twitter=None, website=None, timestamp=None):
        self.page_id = page_id
        self.name = name
        self.comment = comment
        self.email = email
        self.twitter = twitter
        self.website = website

        if timestamp is None:
            self.timestamp = datetime.utcnow()

    def __repr__(self):
        return '<Comment on Page(%s)>' % self.page.title

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
    'revisions': dynamic_loader(Revision,
                    backref='page',
                    order_by=revisions_table.c.revision_id.desc()
    ),
    'comments': dynamic_loader(Comment,
                    backref='page',
                    order_by=comments_table.c.comment_id.asc()
    )
})
mapper(Comment, comments_table)
mapper(Revision, revisions_table)
mapper(UrlMap, urlmaps_table, properties={
    'page': relation(Page)
})
mapper(FouroFour, fourofour_table)
mapper(BlogPages, blogpages_table, properties={
    'page': relation(Page)
})

