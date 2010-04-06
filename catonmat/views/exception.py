#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug                           import Response

from pygments               import highlight
from pygments.lexers        import get_lexer_by_name
from pygments.formatters    import HtmlFormatter
from pygments.lexers.agile  import PythonTracebackLexer

from catonmat.views.utils               import render_template
from catonmat.errorlog                  import str_traceback

import sys

# ----------------------------------------------------------------------------

def main(request):
    exc_type, exc_value, tb = sys.exc_info()
    str_tb = str_traceback(exc_type, exc_value, tb)

    highlighted_str_tb = highlight(str_tb, PythonTracebackLexer(), HtmlFormatter())

    template = render_template('exception',
                 exception_type=exc_type.__name__,
                 exception_message=str(exc_value),
                 traceback=highlighted_str_tb)
    return Response(template, mimetype='text/html', status=500)

