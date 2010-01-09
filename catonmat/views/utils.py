#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website. See this post for more info:
# http://www.catonmat.net/blog/50-ideas-for-the-new-catonmat-website/
#
# Code is licensed under GNU GPL license.
#

from werkzeug        import import_string
from mako.template   import Template
from mako.lookup     import TemplateLookup

from catonmat.quotes import get_random_quote
from catonmat.config import config

# ----------------------------------------------------------------------------

def get_view(endpoint):
  try:
    return import_string('catonmat.views.' + endpoint)
  except (ImportError, AttributeError):
    try:
      return import_string(endpoint)
    except (ImportError, AttributeError):
      raise RuntimeError('Could not locate view for %r' % endpoint)

mako_lookup = TemplateLookup(
    directories=['catonmat/templates'], output_encoding='utf-8'
)

def render_template_with_quote(template_name, template_args=None):
    if template_args is None:
        template_args = {}
    template = get_template(template_name)
    quote = get_random_quote()
    return template.render(quote=quote, **template_args)

def get_template(name):
    file = name + ".tmpl.html"
    template = mako_lookup.get_template(file)
    return template

