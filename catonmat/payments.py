#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug import Response
from catonmat.models import PayPalPayments

def awk_book(request):
    PayPalPayments('awk_book', request).save()
    return Response('ok')

def awk_book_shantanu(request):
    PayPalPayments('awk_book_shantanu', request).save()
    return Response('ok')

def sed_book(request):
    PayPalPayments('sed_book', request).save()
    return Response('ok')

