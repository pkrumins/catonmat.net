#!/usr/bin/python
#

from werkzeug import run_simple
from catonmat.application import application

run_simple('0.0.0.0', 5000, application,
    use_debugger=True, use_reloader=True)

