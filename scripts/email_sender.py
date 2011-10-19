#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# The new catonmat.net website.
#
# Code is licensed under GNU GPL license.
#

import sys
sys.path.append('.')

import smtplib, time, urllib, urllib2, socket, subprocess
import simplejson as json
from datetime import datetime
from email import encoders
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from unidecode import unidecode

MailServer = "localhost"
MailFrom = "Peteris Krumins <peter@catonmat.net>"
Subject = "I have written my second e-book: Sed One-Liners Explained!"

def template_replace(text, hash):
    for x in hash:
        text = text.replace("!%s!" % x, hash[x])
    return text


def send_mail(mail_to, mail_from, subject, body):
    TO = [mail_to]

    mail = MIMEText(body.encode('utf8'), 'plain')
    mail['Subject'] = subject
    mail['From'] = mail_from
    mail['To'] = ','.join(TO)

    server = smtplib.SMTP(MailServer)
    server.sendmail(mail_from, TO, mail.as_string())
    server.quit()


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        print "Usage: script.py emails_file template_file"
        sys.exit(1)

    emails_file, template_file = args

    fh = open(emails_file)
    emails = fh.read()
    fh.close()

    fh = open(template_file)
    template = fh.read()
    fh.close()

    emails = [e for e in emails.split('\n') if e]
    for e in emails:
        name, surname, email = e.split('\t')
        etemplate = template_replace(template, {
            "NAME" : name,
            "SURNAME" : surname
        })
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        print "[%s] Sending email to %s %s (%s)." % (now, unidecode(name), unidecode(surname), email)
        send_mail(email, MailFrom, Subject, etemplate)
        time.sleep(10)

