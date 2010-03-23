#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

import sys
sys.path.append('/home/pkrumins/catonmat')

from tests.page_comment_tests import run_parser_tests
from catonmat.parser import parse_comment

# ---------------------------------------------------------------------------

PATH = '/home/pkrumins/catonmat/tests/comment-parser'

def run_tests():
    success = run_parser_tests(PATH, parse_comment)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()

