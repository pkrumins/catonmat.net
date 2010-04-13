#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug.exceptions            import NotFound

from catonmat.models                import News, session
from catonmat.views.utils           import cached_template_response, render_template

# ----------------------------------------------------------------------------

def main(request):
    return cached_template_response(
             compute_main,
             'news',
             3600)

def compute_main():
    news = session.query(News).order_by(News.timestamp.desc()).all()
    return render_template('news', news=news)

