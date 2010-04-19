#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from catonmat.admin             import require_admin, logged_in, REQUIRE_IP
from catonmat.views.utils       import display_plain_template

# ----------------------------------------------------------------------------

@require_admin([REQUIRE_IP])
def main(request):
    if not logged_in(request):
        return display_plain_template('admin/login')
    return display_plain_template('admin/index')

