#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug                   import redirect
from werkzeug.exceptions        import NotFound

from catonmat.models            import ArticleSeries, session
from catonmat.views.utils       import (
    render_template, cached_template_response, number_to_us
)

# ----------------------------------------------------------------------------

def main(request):
    if request.method == "POST":
        return handle_series_post(request)
    return handle_series_get(request)


def handle_series_post(request):
    return redirect(request.form['navigate'])


def handle_series_get(request):
    """ list all series """
    return list(request)


def list(request):
    return cached_template_response(
             compute_list,
             'series', 
             3600)


def compute_list():
    series = session. \
               query(ArticleSeries). \
               order_by(ArticleSeries.name.asc()). \
               all()
    return render_template('series_list', series=series)



def single(request, seo_name):
    """ list articles in single series """
    return cached_template_response(
             compute_single,
             'series_%s' % seo_name,
             3600,
             seo_name)


def compute_single(seo_name):
    series = session.query(ArticleSeries).filter_by(seo_name=seo_name).first()
    if not series:
        # TODO: better not-found message
        raise NotFound
    return render_template('series', series=series, number_to_us=number_to_us)

