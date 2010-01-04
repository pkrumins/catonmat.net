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
    name, email, website, comment = extract_comment(request)
    return foo

def comment_add(request):
    pass

