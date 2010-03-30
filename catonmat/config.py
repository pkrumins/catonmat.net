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
# of circular references.

class MakoDict(object):
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


config = MakoDict({
    'database_uri':     'mysql://catonmat@localhost/catonmat?charset=utf8',
    'database_echo':    True,
    'posts_per_page':   5,
    'use_cache':        True,
    'download_path':    '/home/pkrumins/catonmat/downloads'
})

