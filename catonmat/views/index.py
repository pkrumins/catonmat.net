#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website. See this post for more info:
# http://www.catonmat.net/blog/50-ideas-for-the-new-catonmat-website/
#
# Code is licensed under GNU GPL license.
#

from catonmat.views.utils import get_template
from catonmat.quotes      import get_random_quote

def main(request):
    template = get_template("index")
    quote = get_random_quote()
    return template.render(quote=quote)

