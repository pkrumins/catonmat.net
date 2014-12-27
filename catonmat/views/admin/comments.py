#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from catonmat.models            import session, Comment
from catonmat.admin             import require_admin
from catonmat.views.utils       import display_plain_template

from werkzeug import Response

import re

# ----------------------------------------------------------------------------

@require_admin()
def main(request):
    query = session.query(Comment).order_by(Comment.comment_id.desc());

    if (request.args.get('page')):
        query = query.slice(int(request.args.get('page'))*100, (int(request.args.get('page'))+1)*100)
        all_comments = query
    else:
        all_comments = query.limit(100)
    return display_plain_template('admin/comments', comments=all_comments)

@require_admin()
def delete_comment(request):
    number = re.compile("^[0-9]+$");
    id = request.args.get('id');
    if number.match(id):
        session.query(Comment).filter_by(comment_id=int(id)).delete()

    return Response('foo', mimetype='text/plain')
