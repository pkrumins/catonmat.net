#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# This program pings several blog services to notify them that blog has updated.
#
# Code is licensed under GNU GPL license.
#

import sys
import socket
from xmlrpclib import Server, Error

socket.setdefaulttimeout(5)

services = [
    [ 'FeedBurner', 'http://ping.feedburner.google.com/' ],
    [ 'Google', 'http://blogsearch.google.com/ping/RPC2' ],
    [ 'Weblogs.com', 'http://rpc.weblogs.com/RPC2' ],
    [ 'Moreover', 'http://api.moreover.com/RPC2' ],
    [ 'Syndic8', 'http://ping.syndic8.com/xmlrpc.php'  ],
    [ 'BlogRolling', 'http://rpc.blogrolling.com/pinger/' ],
    [ 'NewsGator', 'http://services.newsgator.com/ngws/xmlrpcping.aspx' ],
    [ 'Blog People', 'http://www.blogpeople.net/servlet/weblogUpdates' ],
    [ 'FeedSky', 'http://www.feedsky.com/api/RPC2' ],
    [ 'Yandex', 'http://ping.blogs.yandex.ru/RPC2' ]
]

default_blog_title  = 'good coders code, great reuse'
default_blog_url    = 'http://www.catonmat.net'
default_blog_fb_url = 'http://feeds.feedburner.com/catonmat'

# ---------------------------------------------------------------------------

def ping_services(blog_title, blog_url, blog_fb_url):
    for service in services:
        ping_service(service, blog_title, blog_url, blog_fb_url)

def ping_service(service, blog_title, blog_url, blog_fb_url):
    service_name, service_url = service
    if service_name == 'FeedBurner': # feedburner is an exception
        blog_url = blog_fb_url
    try:
        print "Pinging %s." % service_name
        rpc = Server(service_url)
        response = rpc.weblogUpdates.ping(blog_title, blog_url)
        if response['flerror']:
            print "Failed pinging %s. Error: %s" % (service_name, response['message'])
        else:
            print "Successfully pinged %s. Response: %s" % (service_name, response['message'])
    except socket.timeout:
        print "Failed pinging %s. Error: socket timed out"
    except Error, e:
        print "Failed pinging %s. Error: %s" % (service_name, str(e))

def main():
    args = sys.argv[1:]
    if len(args) != 0 and len(args) != 3:
        print >>sys.stderr, """Usage: %s "blog title" BLOG_URL FEEDBURNER_URL"""
        sys.exit(1)
    if len(args) == 0:
        print "Using default blog data for blog %s" % default_blog_title
        blog_title  = default_blog_title
        blog_url    = default_blog_url
        blog_fb_url = default_blog_fb_url
    if len(args) == 3:
        blog_title, blog_url, blog_fb_url = args
    
    ping_services(blog_title, blog_url, blog_fb_url)

if __name__ == '__main__':
    main()

