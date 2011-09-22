#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from catonmat.models    import FouroFour, Exception
from StringIO           import StringIO

import traceback
import sys

# ----------------------------------------------------------------------------

def log_404(request):
    if request.path.find("/c/") != 0: # don't log comment url 404s
        FouroFour(request).save()


def str_traceback(exc_type, exc_value, tb):
    buffer = StringIO()
    traceback.print_exception(exc_type, exc_value, tb, file=buffer)
    return buffer.getvalue()


def log_exception(request):
    exc_type, exc_value, tb = sys.exc_info()
    str_tb = str_traceback(exc_type, exc_value, tb)
    Exception(request, str(exc_type), str(exc_value), str_tb).save()

