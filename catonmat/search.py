#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from catonmat.thirdparty.sphinxapi          import SphinxClient

# ----------------------------------------------------------------------------

class SearchError(Exception):
    pass


def search(query, index):
    sc = SphinxClient()
    sc.SetServer('localhost', 9312)
    result = sc.Query(query, index)
    if not result:
        raise SearchError(sc.GetLastError())
    return result

