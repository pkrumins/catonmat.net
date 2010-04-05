#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from sqlalchemy.orm  import mapper, sessionmaker, scoped_session
from sqlalchemy      import (
    MetaData,
    Table,    Column,   ForeignKey,
    String,   Text,     Integer,        DateTime,   Boolean,    LargeBinary,
    create_engine
)

from catonmat.config import config

# ----------------------------------------------------------------------------

metadata = MetaData()
engine = create_engine(
    config['database_uri'],
    echo=config['database_echo'],
    pool_recycle=3600
)

Session = sessionmaker(bind=engine, autoflush=True, autocommit=False)
session = scoped_session(Session)

pages_table = Table('pages', metadata,
    Column('page_id',       Integer,    primary_key=True),
    Column('title',         String(256)),
    Column('created',       DateTime),
    Column('last_update',   DateTime),
    Column('content',       Text),
    Column('excerpt',       Text),      # goes in <meta description="...">
    Column('category_id',   Integer,    ForeignKey('categories.category_id')),
    Column('views',         Integer),   # should factor out to pagemeta_table
    mysql_charset='utf8'
)

pagemeta_table = Table('page_meta', metadata,
    Column('meta_id',       Integer,     primary_key=True),
    Column('page_id',       Integer,     ForeignKey('pages.page_id')),
    Column('meta_key',      String(128)),
    Column('meta_val',      LargeBinary),
    mysql_charset='utf8'
)

revisions_table = Table('revisions', metadata,
    Column('revision_id',   Integer,    primary_key=True),
    Column('page_id',       Integer,    ForeignKey('pages.page_id')),
    Column('timestamp',     DateTime),
    Column('change_note',   Text),
    Column('title',         String(256)),
    Column('content',       Text),
    Column('excerpt',       Text),
    mysql_charset='utf8'
)

comments_table = Table('comments', metadata,
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

categories_table = Table('categories', metadata,
    Column('category_id',   Integer,     primary_key=True),
    Column('name',          String(128)),
    Column('seo_name',      String(128), unique=True),
    Column('description',   Text),
    Column('count',         Integer),    # number of pages in this category
)

tags_table = Table('tags', metadata,
    Column('tag_id',        Integer,     primary_key=True),
    Column('name',          String(128)),
    Column('seo_name',      String(128), unique=True),
    Column('description',   Text),
    Column('count',         Integer),    # number of pages tagged
)

page_tags_table = Table('page_tags', metadata,
    Column('page_id',       Integer,    ForeignKey('pages.page_id')),
    Column('tag_id',        Integer,    ForeignKey('tags.tag_id'))
)

urlmaps_table = Table('url_maps', metadata,
    Column('url_map_id',    Integer,     primary_key=True),
    Column('request_path',  String(256), unique=True),
    Column('page_id',       Integer,     ForeignKey('pages.page_id')),
    mysql_charset='utf8'
)

redirects_table = Table('redirects', metadata,
    Column('redirect_id',   Integer,     primary_key=True),
    Column('old_path',      String(256), unique=True),
    Column('new_path',      String(256)),
    Column('code',          Integer),
    mysql_charset='utf8'
)

fourofour_table = Table('404', metadata,
    Column('404_id',        Integer,    primary_key=True),
    Column('request_path',  Text),
    Column('date',          DateTime),
    Column('visitor_id',    Integer,    ForeignKey('visitors.visitor_id')),
    mysql_charset='utf8'
)

exceptions_table = Table('exceptions', metadata,
    Column('exception_id',  Integer,    primary_key=True),
    Column('request_path',  Text),
    Column('traceback',     Text),
    Column('last_error',    Text),
    Column('date',          DateTime),
    Column('visitor_id',    Integer,    ForeignKey('visitors.visitor_id')),
    mysql_charset='utf8'
)

blogpages_table = Table('blog_pages', metadata,
    Column('blog_page_id',  Integer,    primary_key=True),
    Column('page_id',       Integer,    ForeignKey('pages.page_id')),
    Column('publish_date',  DateTime),
    Column('visible',       Boolean),
    mysql_charset='utf8'
)

visitors_table = Table('visitors', metadata,
    Column('visitor_id',    Integer,    primary_key=True),
    Column('ip',            String(39)),
    Column('host',          String(256)),
    Column('headers',       Text),
    Column('timestamp',     DateTime),
    mysql_charset='utf8'
)

rss_table = Table('rss', metadata,
    Column('rss_id',        Integer,    primary_key=True),
    Column('page_id',       Integer,    ForeignKey('pages.page_id')),
    Column('publish_date',  DateTime),
    Column('visible',       Boolean),
    mysql_charset='utf8'
)

downloads_table = Table('downloads', metadata,
    Column('download_id',   Integer,    primary_key=True),
    Column('title',         String(128)),
    Column('filename',      String(128)),
    Column('mimetype',      String(64)),
    Column('timestamp',     DateTime),
    Column('downloads',     Integer),
    mysql_charset='utf8'
)

download_stats_table = Table('download_stats', metadata,
    Column('stat_id',       Integer,    primary_key=True),
    Column('download_id',   Integer,    ForeignKey('downloads.download_id')),
    Column('ip',            String(39)),
    Column('timestamp',     DateTime),
)

feedback_table = Table('feedback', metadata,
    Column('feedback_id',   Integer,    primary_key=True),
    Column('visitor_id',    Integer,    ForeignKey('visitors.visitor_id')),
    Column('name',          String(64)),
    Column('email',         String(128)),
    Column('website',       String(256)),
    Column('subject',       Text),
    Column('message',       Text),
    Column('timestamp',     DateTime),
    mysql_charset='utf8'
)

