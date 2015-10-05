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

def awk_book_995(request):
    PayPalPayments('awk_book_995', request).save()
    return Response('ok')

def awk_book_shantanu(request):
    PayPalPayments('awk_book_shantanu', request).save()
    return Response('ok')

def sed_book(request):
    PayPalPayments('sed_book', request).save()
    return Response('ok')

def sed_book_shantanu(request):
    PayPalPayments('sed_book_shantanu', request).save()
    return Response('ok')

def perl_book(request):
    PayPalPayments('perl_book', request).save()
    return Response('ok')

def june_giveaway(request):
    if not 'secret' in request.form:
        return Response('secret missing', 400);

    if request.form['secret'] != "secret":
        return Response('wrong secret', 400);

    if not 'first_name' in request.form:
        return Response('first_name missing', 400);

    if not 'last_name' in request.form:
        return Response('last_name missing', 400);

    if not 'payer_email' in request.form:
        return Response('payer_email missing', 400);

    PayPalPayments('awk_book_june', request).save()
    return Response('ok')
