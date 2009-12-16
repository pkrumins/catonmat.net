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

from catonmat.database import Metadata, Engine

def init_database():
    Metadata.create_all(Engine)

print "Initing catonmat database."
init_database()
print "Done initing."

