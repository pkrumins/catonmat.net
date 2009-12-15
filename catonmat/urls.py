#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# Code is licensed under MIT license.
#

import re

from catonmat.models  import UrlMap
from werkzeug.routing import Map, Rule as RuleBase, Submount

def get_page_from_request(request):
    request_path = request.path.rstrip('/')
    request_path = re.sub('//+', '/', request_path)

    return UrlMap.query.filter_by(request_path=request_path).first()

class Rule(RuleBase):
    def __gt__(self, endpoint):
        self.endpoint = endpoint
        return self

url_map = Map([
    Rule('/')                   > 'index.main',
    Rule('/quotes')             > 'quotes.main',
    Rule('/download/<file>')    > 'downloads.main'
])

