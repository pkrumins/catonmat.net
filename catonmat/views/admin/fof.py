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
from catonmat.models            import session, FouroFour
from catonmat.views.utils       import display_plain_template

# ----------------------------------------------------------------------------

@require_admin()
def main(request):
    fof = session.query(FouroFour).order_by(FouroFour.date.desc()).all()
    return display_plain_template('admin/404', fof=fof)

