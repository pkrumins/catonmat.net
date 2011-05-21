#!/usr/bin/python
#

import sys
from werkzeug import run_simple
from catonmat.application import application

port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
run_simple('0.0.0.0', port, application,
    use_debugger=True, use_reloader=True)

