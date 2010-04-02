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

from catonmat.models   import FouroFour, Exception

def log_404(request):
    fof = FouroFour(request)
    fof.save()

def log_exception(request, e):
    last_error = str(e)
    print "---------------------"
    print last_error
    print "---------------------"

