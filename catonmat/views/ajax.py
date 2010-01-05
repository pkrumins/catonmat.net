#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from catonmat.models import Comment

import simplejson as json

# todo: factor comment stuff out to comments.py

class CommentError(Exception):
    pass

def comment_validate(name, email, website, comment):
    if not len(name.strip()):
        raise CommentError, "No name specified"
    if not len(email.strip()):
        raise CommentError, "No e-mail specified"
    if not len(comment.strip()):
        raise CommentError, "The comment is empty"

def extract_comment(request):
    fields = ['name', 'email', 'website', 'comment']
    return [request.args[x] for x in fields]

def comment_preview(request):
    try:
        fields = ['name', 'email', 'website', 'comment']
        comment_validate(*[request.form[x] for x in fields])
    except CommentError, e:
        return json.dumps({'status': 'error', 'msg': e.message})

    return json.dumps({'status': 'success', 'comment': request.form['comment']})

def comment_add(request):
    pass

