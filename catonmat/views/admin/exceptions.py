#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from catonmat.admin             import require_admin
from catonmat.models            import session, Exception
from catonmat.views.utils       import display_plain_template

# ----------------------------------------------------------------------------

@require_admin()
def main(request):
    exc = session.query(Exception).order_by(Exception.date.desc()).all()
    return display_plain_template('admin/exceptions', exc=exc)

