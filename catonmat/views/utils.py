#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from werkzeug        import import_string, Response

from mako.template   import Template
from mako.lookup     import TemplateLookup

from catonmat.quotes import get_random_quote
from catonmat.config import config

# ----------------------------------------------------------------------------

class MakoDict(object):
    """
    Given a dict d, MakoDict makes its keys accessible via dot.
    It also returns None if the key doesn't exist.
    >>> d = DotDict({'apple': 5, 'peach': { 'kiwi': 9 } })
    >>> d.apple
    5
    >>> d.peach.kiwi
    9
    >>> d.coco
    None
    """
    def __init__(self, d):
        for k, v in d.items():
            if isinstance(v, dict):
                v = MakoDict(v)
            self.__dict__[k] = v

    def __getattr__(self, name):
        return None


mako_lookup = TemplateLookup(
    directories=['catonmat/templates'], output_encoding='utf-8'
)


def display_template_with_quote(template, template_data):
    return Response(
        render_template_with_quote(template, **template_data),
        mimetype='text/html'
    )


def render_template_with_quote(template_name, **template_args):
    template = get_template(template_name)
    quote = get_random_quote()
    return template.render(quote=quote, **template_args), 'text/html'


def get_template(name):
    file = name + ".tmpl.html"
    template = mako_lookup.get_template(file)
    return template


def get_view(endpoint):
  try:
    return import_string('catonmat.views.' + endpoint)
  except (ImportError, AttributeError):
    try:
      return import_string(endpoint)
    except (ImportError, AttributeError):
      raise RuntimeError('Could not locate view for %r' % endpoint)

