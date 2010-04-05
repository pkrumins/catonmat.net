#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from sqlalchemy.orm         import dynamic_loader, relation, mapper

from catonmat.views.utils   import number_to_us
from catonmat.database      import (
    pages_table,     revisions_table, urlmaps_table,    fourofour_table,
    blogpages_table, comments_table,  categories_table, tags_table,
    page_tags_table, visitors_table,  rss_table,        pagemeta_table,
    downloads_table, redirects_table, feedback_table,   exceptions_table,
    download_stats_table,
    session
)

from urlparse               import urlparse
from datetime               import datetime

import hashlib

# ----------------------------------------------------------------------------

class ModelBase(object):
    def save(self):
        session.add(self)
        session.commit()


class Page(ModelBase):
    def __init__(self, title, content=None, excerpt=None, created=None, last_update=None, category_id=None, views=0):
        self.title = title
        self.content = content
        self.excerpt = excerpt
        self.created = created
        self.last_update = last_update
        self.category_id = category_id
        self.views = views
        
        if self.created is None:
            self.created = datetime.utcnow()
        if self.last_update is None:
            self.last_update = datetime.utcnow()

    @property
    def parsed_content(self):
        from catonmat.parser import parse_page
        return parse_page(self.content)

    @property
    def publish_time(self):
        if self.blog_page:
            return self.blog_page.publish_date.strftime("%B %d, %Y")
        return None

    @property
    def comment_count(self):
        return session.query(Comment).filter_by(page_id=self.page_id).count()

    @property
    def request_path(self):
        if self.url_map:
            return self.url_map.request_path
        return None

    @property
    def us_views(self):
        return number_to_us(self.views)

    def add_tag(self, tag):
        real_tag = tag
        t = session.query(Tag).filter_by(seo_name=tag.seo_name).first()
        if t:
            real_tag = t
        self.tags.append(real_tag)
        real_tag.count += 1

    def add_comment(self, comment):
        self.comments.append(comment)

    def __repr__(self):
        return '<Page: %s>' % self.title


class PageMeta(ModelBase):
    def __init__(self, page_id, meta_key, meta_val):
        self.page_id  = page_id
        self.meta_key = meta_key
        self.meta_val = meta_val

    def __repr__(self):
        return '<PageMeta(%s) for Page(id=%s)' % (self.meta_key, self.page_id)


class Revision(ModelBase):
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


class Comment(ModelBase):
    def __init__(self, page_id, name, comment, visitor, parent_id=None, email=None, twitter=None, website=None, timestamp=None):
        self.page_id = page_id
        self.parent_id = parent_id
        self.name = name
        self.comment = comment
        self.email = email
        self.gravatar_md5 = ""
        self.twitter = twitter
        self.website = website
        self.visitor = visitor
        self.timestamp = timestamp

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
        from catonmat.parser import parse_comment
        return parse_comment(self.comment)

    @property
    def publish_time(self):
        return self.timestamp.strftime("%B %d, %Y, %H:%M")

    def __repr__(self):
        return '<Comment(%d) on Page(%s)>' % (self.comment_id, self.page.title)


class Category(ModelBase):
    def __init__(self, name, seo_name, description=None, count=0):
        self.name = name
        self.seo_name = seo_name
        self.description = description
        self.count = count

    @property
    def blog_pages(self): # TODO: Don't know to make it via dynamic_loader
       return session. \
                query(Page). \
                join(BlogPage). \
                filter(Page.category_id==self.category_id)

    def __repr__(self):
        return '<Category %s>' % self.name


class Tag(ModelBase):
    def __init__(self, name, seo_name, description=None, count=0):
        self.name = name
        self.seo_name = seo_name
        self.description = description
        self.count = count

    def __repr__(self):
        return '<Tag %s>' % self.name


class UrlMap(ModelBase):
    def __init__(self, request_path, page_id):
        self.request_path = request_path
        self.page_id  = page_id

    def __repr__(self):
        return '<UrlMap from %s to Page(%s)>' % (self.request_path, self.page.title)


class Redirect(ModelBase):
    def __init__(self, old_path, new_path, code=301):
        self.old_path = old_path
        self.new_path = new_path
        self.code     = code

    def __repr__(self):
        return '<Redirect from %s to %s (%d)>' % (self.old_path, self.new_path, self.code)


class FouroFour(ModelBase):
    def __init__(self, request):
        self.request_path = request.path
        self.visitor = Visitor(request)
        self.date = datetime.utcnow()

    def __repr__(self):
        return '<404 of %s>' % self.request_path


class Exception(ModelBase):
    def __init__(self, request, traceback, last_error):
        self.request_path = request.path
        self.traceback = traceback
        self.last_error = last_error
        self.visitor = Visitor(request)
        self.date = datetime.utcnow()

    def __repr__(self):
        return '<Exception: %s>' % self.last_error


class BlogPage(ModelBase):
    def __init__(self, page, publish_date=None, visible=True):
        self.page = page
        self.publish_date = publish_date
        self.visible = visible

        if publish_date is None:
            self.publish_date = date.utcnow()

    def __repr__(self):
        return '<Blog Page of Page(%s)>' % page.title


class Visitor(ModelBase):
    def __init__(self, request):
        self.ip = request.remote_addr
        self.headers = str(request.headers).strip()
        self.host = None
        self.timestamp = datetime.utcnow()

    def __repr__(self):
        return '<Visitor from %s>' % ip


class Rss(ModelBase):
    def __init__(self, page, publish_date, visible=True):
        self.page = page
        self.publish_date = publish_date
        self.visible = visible

    def __repr__(self):
        return '<RSS for Page(%s)>' % page.title


class Download(ModelBase):
    def __init__(self, title, filename, mimetype=None, downloads=0, timestamp=None):
        self.title = title
        self.filename = filename
        self.mimetype = mimetype
        self.downloads = downloads
        if timestamp is None:
            self.timestamp = datetime.utcnow()

    def another_download(self, request):
        self.downloads = Download.downloads + 1 # this creates an update statement
        download_stat = DownloadStats(self, request.remote_addr)
        self.save()
        download_stat.save()

    @property
    def us_downloads(self):
        return number_to_us(self.downloads)

    def __repr__(self):
        return '<Download %s>' % self.filename


class DownloadStats(ModelBase):
    def __init__(self, download, ip, timestamp=None):
        self.download = download
        self.ip = ip
        if timestamp is None:
            self.timestamp = datetime.utcnow()

    def __repr__(self):
        return '<DownloadStat of %s>' % self.download.filename


class Feedback(ModelBase):
    def __init__(self, visitor, name, email, subject, message, website=None):
        self.visitor = visitor
        self.name = name
        self.email = email
        self.subject = subject
        self.message = message
        self.website = website
        self.timestamp = datetime.utcnow()

    def __repr__(self):
        return '<Feedback from %s>' % self.name


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
                    order_by=tags_table.c.seo_name
    ),
    'properties': dynamic_loader(
                    PageMeta,
                    backref='page',
                    order_by=pagemeta_table.c.meta_id
    ),
    'url_map':   relation(UrlMap, uselist=False),
    'blog_page': relation(BlogPage, uselist=False),
    'rss_page':  relation(Rss, uselist=False)
})
mapper(PageMeta, pagemeta_table)
mapper(Revision, revisions_table)
mapper(Comment,  comments_table, properties={
    'visitor': relation(Visitor, uselist=False)
})
mapper(Category, categories_table)
mapper(Tag,      tags_table, properties={
    'pages': dynamic_loader(Page, secondary=page_tags_table)
})
mapper(UrlMap, urlmaps_table, properties={
    'page': relation(Page, uselist=False)
})
mapper(Redirect, redirects_table)
mapper(FouroFour, fourofour_table, properties={
    'visitor': relation(Visitor, uselist=False)
})
mapper(Exception, exceptions_table, properties={
    'visitor': relation(Visitor, uselist=False)
})
mapper(BlogPage, blogpages_table, properties={
    'page': relation(Page, uselist=False)
})
mapper(Rss, rss_table, properties={
    'page': relation(Page)
})
mapper(Visitor, visitors_table)
mapper(Download, downloads_table, properties={
    'stats': dynamic_loader(
                DownloadStats,
                backref='download',
                order_by=download_stats_table.c.stat_id.asc()
    )
})
mapper(DownloadStats, download_stats_table)
mapper(Feedback, feedback_table, properties={
    'visitor': relation(Visitor, uselist=False)
})

