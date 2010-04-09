#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

# copied MakoDict from catonmat.views.utils because I couldn't get rid
# of circular references. Also renamed it to MakoDictz for great justice.

class MakoDictz(object):
    """
    Given a dict d, MakoDict makes its keys accessible via dot.
    It also returns None if the key doesn't exist.
    >>> d = DotDict({'apple': 5, 'peach': { 'kiwi': 9 } })
    >>> d.apple
    5
    >>> d.peach.kiwi
    9
    >>> d.coco
    None
    """
    def __init__(self, d, exclude=None):
        if exclude is None:
            exclude = []

        for k, v in d.items():
            if isinstance(v, dict) and k not in exclude:
                v = MakoDict(v)
            self.__dict__[k] = v

    def __getitem__(self, k):
        return self.__dict__[k]

    def __getattr__(self, name):
        return None

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __setitem__(self, name, value):
        self.__dict__[name] = value


config = MakoDictz({
    'database_uri':     'mysql://catonmat@localhost/catonmat?charset=utf8',
    'database_echo':    False,
    'posts_per_page':   5,
    'use_cache':        False,
    'download_path':    '/home/pkrumins/catonmat/downloads',
    'rss_items':        20,
    'mako_modules':     '/home/pkrumins/catonmat/mako_modules'
})

