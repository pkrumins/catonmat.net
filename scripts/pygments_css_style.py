#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# This program imports a wordpress database into the new catonmat database
#
# Code is licensed under GNU GPL license.
#

import sys
from pygments.formatters import HtmlFormatter
from pygments.util       import ClassNotFound

def print_style(name):
    try:
        print HtmlFormatter(style=name).get_style_defs('.highlight')
    except ClassNotFound:
        print "Style %s not found!" % name
        sys.exit(1)

def main():
    args = sys.argv[1:]
    if not args:
        print "Usage: %s <style name>" % sys.argv[0]
        sys.exit(1)
    style_name = args[0]
    print_style(style_name)

if __name__ == "__main__":
    main()

