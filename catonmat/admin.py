#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug.contrib.securecookie  import SecureCookie

from catonmat.views.utils           import display_template
from catonmat.config                import config

import hashlib

# ----------------------------------------------------------------------------

REQUIRE_IP   = 1
REQUIRE_CRED = 2

def require_admin(req_what=[REQUIRE_IP, REQUIRE_CRED]):
    def _require_admin(f):        
        def __require_admin(request, *args, **kw):
            if not req_what:
                raise ValueError, "Forgot to specify req_what in %s" % f.__name__
            if REQUIRE_IP in req_what:
                if not allowed_ip(request):
                    return display_template('admin/access_denied',
                             message='your ip %s was not in the allowed ip list' % str(request.remote_addr))
            if REQUIRE_CRED in req_what:
                if not admin_cred_match(request):
                    return display_template('admin/access_denied',
                             message='admin credentials don\'t match')
            return f(request, *args, **kw)
        return __require_admin
    return _require_admin

def unserialize_secure_cookie(request):
    if not request.cookies.get('admin'):
        return dict()
    return SecureCookie.unserialize(request.cookies.get('admin'), secret_key=config.secure_key)

def admin_cred_match(request):
    d = unserialize_secure_cookie(request)
    if not d.get('admin_user'):
        return False
    if not d.get('admin_hash'):
        return False
    return admin_cred_match_prim(d.get('admin_user'), d.get('admin_hash'))

def admin_cred_match_prim(user, hash):
    return user == get_admin_user() and hash == get_admin_hash() 

def get_admin_user():
    return open(config.admin_hash_file).readline().strip().split(':')[0]

def get_admin_hash():
    return open(config.admin_hash_file).readline().strip().split(':')[1]

def allowed_ip(request):
    return request.remote_addr in get_allowed_ips()

def get_allowed_ips():
    return [l.strip() for l in open(config.ips_file, 'r')]

def logged_in(request):
    return admin_cred_match(request)

def hash_password(password):
    md5 = hashlib.md5()
    md5.update(password)
    md5.update(config.secure_key)
    return md5.hexdigest()

def mk_secure_cookie(Dict):
    return SecureCookie(Dict, secret_key=config.secure_key)

