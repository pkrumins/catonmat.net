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

from BeautifulSoup import BeautifulSoup as BS
from catonmat.parser import parse_page
import os

def slurp_file(filename):
    return file(filename).read()

def empty_list_nl(things):
    return not [t for t in things if t != '\n' and t != '\r' and t != '\r\n']

def equal(thing1, thing2):
    if isinstance(thing1, basestring) and isinstance(thing2, basestring):
        stripped_thing1 = thing1.replace('\r', '').replace('\n', '')
        stripped_thing2 = thing2.replace('\r', '').replace('\n', '')
        return stripped_thing1 == stripped_thing2
    if isinstance(thing1, basestring) or isinstance(thing2, basestring):
        return False
    return equal_bs(thing1.contents, thing2.contents)

def equal_bs(bs1, bs2):
    if empty_list_nl(bs1) and empty_list_nl(bs2):
        return True
    if empty_list_nl(bs1) or empty_list_nl(bs2):
        return False
    return equal(bs1[0], bs2[0]) and \
            equal_bs(bs1[1:], bs2[1:])

def run_page_parser_tests():
    success = True
    path_to_files = '/home/pkrumins/catonmat/tests/page-parser'
    test_files = os.listdir(path_to_files)
    input_files = sorted(f for f in test_files if f.endswith('.input'))
    for input_file in input_files:
        input_file_path = os.path.join(path_to_files, input_file)
        output_file_path = input_file_path.replace('.input', '.output')

        input = slurp_file(input_file_path)
        
        parsed_input = parse_page(input)
        expected_output = slurp_file(output_file_path)

        input_bs =  BS(parsed_input)
        output_bs = BS(expected_output)

        status = equal_bs(input_bs.contents, output_bs.contents)

        if status:
            print "Success: %s." % input_file
        else:
            print "Failed: %s." % input_file
            success = False
    return success

def run_tests():
    success = run_page_parser_tests()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()

