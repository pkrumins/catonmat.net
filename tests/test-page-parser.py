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

def simplify_bs(bs):
    ret = []
    for item in bs:
        if isinstance(item, basestring):
            item = item.strip()
            if item:
                ret.append(item.replace('\r', '').replace('\n', ''))
        else:
            ret.append([item.name, simplify_bs(item.contents)])
    return ret

def equal_bs(bs1, bs2):
    return bs1 == bs2

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

        simplified_input_bs = simplify_bs(input_bs)
        simplified_output_bs = simplify_bs(output_bs)

        status = equal_bs(simplified_input_bs, simplified_output_bs)

        if status:
            print "Success: %s." % input_file
        else:
            print "Failed: %s." % input_file
            print "Expected:", simplified_output_bs
            print "Got:", simplified_input_bs
            success = False
    return success

def run_tests():
    success = run_page_parser_tests()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()

