#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# This script creates all the new catonmat.net database tables.
#
# Code is licensed under GNU GPL license.
#

import sys
sys.path.append('/home/pkrumins/catonmat')

from catonmat.database import metadata, engine

def init_database():
    metadata.create_all(engine)

print "Initing catonmat database."
init_database()
print "Done initing."

