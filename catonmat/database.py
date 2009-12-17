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

from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    DateTime, Integer, Text, Boolean, String,
    create_engine
)
from sqlalchemy.orm import scoped_session, create_session
from sqlalchemy.orm import mapper as sqla_mapper
from catonmat.config import config

Metadata = MetaData()
Engine = create_engine( config['database_uri'],
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
    mysql_charset='utf8'
)

revisions_table = Table('revisions', Metadata,
    Column('revision_id',   Integer,    primary_key=True),
    Column('page_id',       Integer,    ForeignKey('pages.page_id')),
    Column('timestamp',     DateTime),
    Column('change_note',   Text),
    Column('title',         String(256)),
    Column('content',       Text),
    mysql_charset='utf8'
)

urlmaps_table = Table('url_maps', Metadata,
    Column('url_map_id',    Integer,     primary_key=True),
    Column('request_path',  String(128), unique=True),
    Column('page_id',       Integer,     ForeignKey('pages.page_id')),
    Column('handler',       String(128)),
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

