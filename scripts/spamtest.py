import sys
sys.path.append('.')

from catonmat.models import Comment
from catonmat.database import session
from catonmat.comment_spamlist import spamlist_names, spamlist_urls, spamlist_emails, spamlist_comments

comments = session.query(Comment).all()

for c in comments:
    for r in spamlist_names:
        if r.search(c.name):
            print "Comment %d matches name %s" % (c.comment_id, c.name.encode('utf8'))

    for r in spamlist_emails:
        if r.search(c.email):
            print "Comment %d matches email %s" % (c.comment_id, c.email)

    for r in spamlist_urls:
        if r.search(c.website):
            print "Comment %d matches website %s" % (c.comment_id, c.website)

    for r in spamlist_comments:
        if r.search(c.comment):
            print "Comment %d matches comment %s..." % (c.comment_id, c.comment[0:50])
