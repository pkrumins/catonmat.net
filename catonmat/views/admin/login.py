#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug                   import redirect

from catonmat.views.utils       import display_plain_template
from catonmat.admin             import (
    require_admin, REQUIRE_IP, hash_password, admin_cred_match_prim,
    mk_secure_cookie
)

# ----------------------------------------------------------------------------

@require_admin([REQUIRE_IP])
def main(request):
    if request.method != "POST":
        return display_plain_template('admin/login', message="Not a POST request")
    
    user = request.form.get('a')
    hash = hash_password(request.form.get('b'))
    if admin_cred_match_prim(user, hash):
        cookie = {
            'admin_user': user,
            'admin_hash': hash
        }
        response = redirect('/admin')
        response.set_cookie('admin', mk_secure_cookie(cookie).serialize(), httponly=True)
        return response

    return display_plain_template('admin/login', message="Password incorrect")

