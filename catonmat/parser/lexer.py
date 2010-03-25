#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

from pygments               import highlight
from pygments.util          import ClassNotFound
from pygments.token         import Token
from pygments.lexer         import RegexLexer
from pygments.lexers        import get_lexer_by_name
from pygments.formatters    import HtmlFormatter

from catonmat.parser.util   import tag_type_by_name, get_lexer
from catonmat.models        import Download
import re

# ----------------------------------------------------------------------------

class DocumentLexer(RegexLexer):
    def open_tag_handler_yielder(lexer, tag_name, full_tag):
        tag_type = tag_type_by_name(tag_name)
        return 0, tag_type, full_tag.lower()

    def open_tag_handler(lexer, match):
        tag_name = match.group(1)
        yield lexer.open_tag_handler_yielder(tag_name, match.group(0))

    def pure_pre_token_stream(lexer, pre_text):
        yield_items = [
            (Token.Tag.BlockTag, "<pre>"),
            (Token.Text, pre_text.replace('<', '&lt;')),
            (Token.Tag.Close, "</pre>")
        ]
        return yield_items

    def pure_pre_handler(lexer, match):
        for token, value in lexer.pure_pre_token_stream(match.group(1)):
            yield 0, token, value

    def lang_pre_handler(lexer, match):
        try:
            lang, code = match.groups()
            lang_lexer = get_lexer_by_name(lang, stripall=True)
            token_stream = get_lexer(highlight(code, lang_lexer, HtmlFormatter()), PreLexer)
        except ClassNotFound:
            token_stream = lexer.pure_pre_token_stream(code)
        for token, value in token_stream:
            yield 0, token, value

    def download_error(lexer, download_id):
        yield_items = [
            (Token.Text, "Oops, download with id %d wasn't found. " \
                         "Please let me know about this error via the " % download_id),
            (Token.Tag.InlineTag, '<a href="/feedback/">'),
            (Token.Text, "feedback"),
            (Token.Tag.Close, "</a>"),
            (Token.Text, " form! Thanks!")
        ]
        return yield_items

    def download_handler(lexer, match):
        download_id = match.group(1)
        download = Download.query.filter_by(download_id=download_id).first()
        if not download:
            token_stream = lexer.download_error(download_id)
        else:
            token_stream = [
                (Token.Tag.InlineTag, '<a href="/download/%s" title="Download %s">' % \
                                        (download.filename, download.title)),
                (Token.Text, download.title),
                (Token.Tag.Close, "</a>")
            ]
        for token, value in token_stream:
            yield 0, token, value

    def download_hits_handler(lexer, match):
        download_id = match.group(1)
        download = Download.query.filter_by(download_id=download_id).first()
        if not download:
            token_stream = lexer.download_error(download_id)
            for token, value in token_stream:
                yield 0, token, value
        else:
            yield 0, Token.Text, download.downloads

    def download_nohits_handler(lexer, match):
        for v in lexer.download_handler(match):
            yield v

    flags = re.IGNORECASE | re.DOTALL
    tokens = {
        'root': [
            (r'\n\n+',               Token.Par),
            (r'\n',                  Token.Br),
            (r'[^<\n]+',             Token.Text),
            (r'<!--.*?-->',          Token.Comment),
            (r'<download#(\d+)#nohits>', download_nohits_handler),
            (r'<download#(\d+)#hits>',   download_hits_handler),
            (r'<download#(\d+)>',        download_handler),
            (r'<pre>(.+?)</pre>',        pure_pre_handler),
            (r'<pre lang="(.+?)">(.+?)</pre>', lang_pre_handler),
            (r'<([a-zA-Z0-9]+).*?>', open_tag_handler),
            (r'</[^>]+>',            Token.Tag.Close)
        ],
    }

class PreLexer(DocumentLexer):
    def pure_pre_token_stream(lexer, pre_text):
        yield_items = [
            (Token.Tag.BlockTag, "<pre>"),
            (Token.Text, pre_text),
            (Token.Tag.Close, "</pre>")
        ]
        return yield_items

from catonmat.parser.commentparser import ALLOWED_COMMENT_TAGS
allowed_open_tag_re = re.compile('|'.join('<(%s)>|<(%s)\W+.*?>' % (tag, tag) for tag in ALLOWED_COMMENT_TAGS))
allowed_close_tag_re = re.compile('|'.join('</(%s)>' % tag for tag in ALLOWED_COMMENT_TAGS))

class CommentLexer(DocumentLexer):
    def open_tag(lexer, _):
        yield 0, Token.Text, '&lt;'

    def comment_open_tag_handler(lexer, match):
        tag_name = [t for t in match.groups() if t][0]
        yield lexer.open_tag_handler_yielder(tag_name, match.group(0))

    tokens = {
        'root': [
            (r'\n\n+',                Token.Par),
            (r'\n',                   Token.Br),
            (r'[^<\n]+',              Token.Text),
            (r'<pre>(.+?)</pre>',     DocumentLexer.pure_pre_handler),
            (r'<pre lang="(.+?)">(.+?)</pre>', DocumentLexer.lang_pre_handler),
            (allowed_open_tag_re,     comment_open_tag_handler),
            (allowed_close_tag_re,    Token.Tag.Close),
            (r'<',                    open_tag)
        ],
    }

