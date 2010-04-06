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
    FouroFour(request).save()

def log_exception(request):
    exc_type, exc_value, tb = sys.exc_info()
    buffer = StringIO()
    traceback.print_exception(exc_type, exc_value, tb, file=buffer)
    Exception(request,
              str(exc_type),
              str(exc_value),
              buffer.getvalue()).save()

