#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from sqlalchemy.orm  import scoped_session, create_session
from sqlalchemy.orm  import mapper as sqla_mapper
from sqlalchemy      import (
    MetaData, Table,    Column, ForeignKey, DateTime, Integer,
    Text,     Boolean,  String, Binary,
    create_engine
)

from catonmat.config import config

# ----------------------------------------------------------------------------

Metadata = MetaData()
Engine = create_engine(
    config['database_uri'],
    convert_unicode=True,
    echo=config['database_echo'],
    pool_recycle=3600
)
Session = scoped_session(
    lambda: create_session(Engine, autoflush=True, autocommit=False)
)

def session_mapper(scoped_session_):
    def mapper(cls, *arg, **kw):
        cls.query = scoped_session_.query_property()
        return sqla_mapper(cls, *arg, **kw)
    return mapper

mapper = session_mapper(Session)

pages_table = Table('pages', Metadata,
    Column('page_id',       Integer,    primary_key=True),
    Column('title',         String(256)),
    Column('created',       DateTime),
    Column('last_update',   DateTime),
    Column('content',       Text),
    Column('excerpt',       Text),      # goes in <meta description="...">
    Column('category_id',   Integer,    ForeignKey('categories.category_id')),
    mysql_charset='utf8'
)

pagemeta_table = Table('page_meta', Metadata,
    Column('meta_id',       Integer,     primary_key=True),
    Column('page_id',       Integer,     ForeignKey('pages.page_id')),
    Column('meta_key',      String(128)),
    Column('meta_val',      Binary),
    mysql_charset='utf8'
)

revisions_table = Table('revisions', Metadata,
    Column('revision_id',   Integer,    primary_key=True),
    Column('page_id',       Integer,    ForeignKey('pages.page_id')),
    Column('timestamp',     DateTime),
    Column('change_note',   Text),
    Column('title',         String(256)),
    Column('content',       Text),
    Column('excerpt',       Text),
    mysql_charset='utf8'
)

comments_table = Table('comments', Metadata,
    Column('comment_id',    Integer,    primary_key=True),
    Column('parent_id',     Integer),
    Column('page_id',       Integer,    ForeignKey('pages.page_id')),
    Column('visitor_id',    Integer,    ForeignKey('visitors.visitor_id')),
    Column('timestamp',     DateTime),
    Column('name',          String(64)),
    Column('email',         String(128)),
    Column('gravatar_md5',  String(32)),
    Column('twitter',       String(128)),
    Column('website',       String(256)),
    Column('comment',       Text),
    mysql_charset='utf8'
)

categories_table = Table('categories', Metadata,
    Column('category_id',   Integer,     primary_key=True),
    Column('name',          String(128)),
    Column('seo_name',      String(128)),
    Column('description',   Text),
    Column('count',         Integer),    # number of pages in this category
)

tags_table = Table('tags', Metadata,
    Column('tag_id',        Integer,    primary_key=True),
    Column('name',          String(128)),
    Column('seo_name',      String(128)),
    Column('description',   Text),
    Column('count',         Integer),    # number of pages tagged
)

page_tags_table = Table('page_tags', Metadata,
    Column('page_id',       Integer,    ForeignKey('pages.page_id')),
    Column('tag_id',        Integer,    ForeignKey('tags.tag_id'))
)

urlmaps_table = Table('url_maps', Metadata,
    Column('url_map_id',    Integer,     primary_key=True),
    Column('request_path',  String(256), unique=True),
    Column('page_id',       Integer,     ForeignKey('pages.page_id')),
    Column('handler',       String(128)),
    Column('redirect',      String(256)),
    mysql_charset='utf8'
)

fourofour_table = Table('404', Metadata,
    Column('404_id',        Integer,    primary_key=True),
    Column('request_path',  Text),
    Column('date',          DateTime),
    mysql_charset='utf8'
)

blogpages_table = Table('blog_pages', Metadata,
    Column('blog_page_id',  Integer,    primary_key=True),
    Column('page_id',       Integer,    ForeignKey('pages.page_id')),
    Column('publish_date',  DateTime),
    Column('visible',       Boolean),
    mysql_charset='utf8'
)

visitors_table = Table('visitors', Metadata,
    Column('visitor_id',    Integer,    primary_key=True),
    Column('ip',            String(15)),
    Column('host',          String(256)),
    Column('headers',       Text),
    Column('timestamp',     DateTime),
    mysql_charset='utf8'
)

rss_table = Table('rss', Metadata,
    Column('rss_id',        Integer,    primary_key=True),
    Column('page_id',       Integer,    ForeignKey('pages.page_id')),
    Column('publish_date',  DateTime),
    Column('visible',       Boolean),
    mysql_charset='utf8'
)

