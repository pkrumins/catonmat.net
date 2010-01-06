#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from catonmat.comments import (
    CommentError, ParseError, validate_comment, parse_comment
)

import simplejson as json

# todo: maybe move all this to comments.py?

def preview_comment(request):
    if request.method == "POST":
        try:
            validate_comment(request)
        except CommentError, e:
            return json.dumps({
                'status':  'error',
                'message': e.message
            })

        try:
            comment = parse_comment(request.form['comment'])
        except ParseError, e:
            return json.dumps({
                'status':  'error',
                'message': e.message
            })

        return json.dumps({
            'status':  'success',
            'comment': comment
        })


def add_comment(request):
    pass
