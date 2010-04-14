#!/usr/bin/python
#

from flup.server.fcgi import WSGIServer
from catonmat.application import application

WSGIServer(application).run()

