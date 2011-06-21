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

from catonmat.models import PayPalPayments, session

PayPalSandbox = False

MailServer = "localhost"
MailFrom = "Peteris Krumins <peter@catonmat.net>"

PayPalUrl = "www.sandbox.paypal.com" if PayPalSandbox else "www.paypal.com"

EmailTemplatePath = "/home/pkrumins/catonmat/payments"
AwkBookPath = "/home/pkrumins/lvm0/Workstation/catonmat/books/awk-one-liners-explained"
LatexLogPath = "/home/pkrumins/catonmat/payments/latex.log"

def template_replace(text, hash):
    for x in hash:
        text = text.replace("!%s!" % x, hash[x])
    return text

def awk_book_template(infile, outfile, payment):
    fd = open("%s/%s" % (AwkBookPath, infile))
    data = fd.read()
    fd.close()

    email = payment.payer_email.replace("_", "\\_")
    data = template_replace(data, {
        "NAME" : payment.first_name,
        "SURNAME" : payment.last_name,
        "EMAIL" : email
    })

    fd = open("%s/%s" % (AwkBookPath, outfile), 'w+')
    fd.write(data.encode('utf-8'))
    fd.close()

def awk_book(payment):
    print "Preparing Awk Book..."
    subject = Products['awk_book']['subject']
    attachment = "%s/%s" % (AwkBookPath, Products['awk_book']['file'])
    attachment_name = Products['awk_book']['attachment_name']
    
    fd = open(EmailTemplatePath + '/thanks-awk-book.txt')
    body = fd.read()
    fd.close()

    email_body = template_replace(body, {
        "NAME": payment.first_name,
        "SURNAME": payment.last_name
    })

    awk_book_template('awkbook_template.tex', 'awkbook.tex', payment)
    awk_book_template('intro_template.tex', 'intro.tex', payment)
    awk_book_template('chapter2_template.tex', 'chapter2.tex', payment)
    awk_book_template('chapter3_template.tex', 'chapter3.tex', payment)
    awk_book_template('chapter4_template.tex', 'chapter4.tex', payment)

    print "Spawning Latex..."
    latex_log = open(LatexLogPath, 'a+')
    latex = subprocess.Popen("pdflatex awkbook.tex", stdout=latex_log, stderr=latex_log, cwd=AwkBookPath, shell=True)
    latex.wait()

    print "Spawning makeindex..."
    makeindex = subprocess.Popen("makeindex awkbook", stdout=latex_log, stderr=latex_log, cwd=AwkBookPath, shell=True)
    makeindex.wait()

    print "Spawning Latex 2nd time..."
    latex = subprocess.Popen("pdflatex awkbook.tex", stdout=latex_log, stderr=latex_log, cwd=AwkBookPath, shell=True)
    latex.wait()

    print "Spawning Latex 3nd time..."
    latex = subprocess.Popen("pdflatex awkbook.tex", stdout=latex_log, stderr=latex_log, cwd=AwkBookPath, shell=True)
    latex.wait()
    latex_log.close()

    print "Sending the Awk book to %s %s (%s)." % (payment.first_name.encode('utf8'), payment.last_name.encode('utf8'), payment.payer_email)
    send_mail(payment.payer_email, MailFrom, Products['awk_book']['subject'], email_body, attachment, attachment_name)


Products = {
    'awk_book': {
        'subject' : 'Your Awk One-Liners Explained E-Book!',
        'file' : 'awkbook.pdf',
        'attachment_name' : 'awk-one-liners-explained.pdf',
        'price' : '5.95',
        'email_body' : 'thanks-awk-book.txt',
        'handler' : awk_book
    }
}


def send_mail(mail_to, mail_from, subject, body, attachment, attachment_name):
    TO = [mail_to]

    mail = MIMEMultipart()
    mail['Subject'] = subject
    mail['From'] = mail_from
    mail['To'] = ','.join(TO)

    mailbody = MIMEText(body, 'plain')
    mail.attach(mailbody)

    fp = open(attachment, 'rb')
    attachment = MIMEBase('application', 'pdf')
    attachment.set_payload(fp.read())
    attachment.add_header('Content-Disposition', 'attachment', filename=attachment_name)
    fp.close()
    encoders.encode_base64(attachment)
    mail.attach(attachment)

    server = smtplib.SMTP(MailServer)
    server.sendmail(mail_from, TO, mail.as_string())
    server.quit()


def payment_already_completed(payment):
    payments = session.query(PayPalPayments) \
        .filter_by(transaction_id=payment.transaction_id) \
        .all()

    for existing_payment in payments:
        if existing_payment.transaction_id == payment.transaction_id:
            if existing_payment.status == 'completed':
                return True
    return False


def valid_paypal_payment(payment):
    PayPalPostUrl = "http://%s/cgi-bin/webscr" % PayPalUrl
    try:
        post_data = json.loads(payment.ipn_message)
        post_data['cmd'] = '_notify-validate'
        post_data = dict([k, v.encode('utf-8')] for k, v in post_data.items())
        response = urllib2.urlopen(PayPalPostUrl, urllib.urlencode(post_data))
        return response.read() == 'VERIFIED'
    except (urllib2.HTTPError, urllib2.URLError), e:
        print "Error POST'ing to PayPal: %s" % str(e)
    except (socket.error, socket.sslerror), e:
        print "Socket error: %s" % str(e)
    except socket.timeout, e:
        print "Socket timeout: %s" % str(e)


def completed_paypal_payment(payment):
    return payment.payment_status == 'Completed'


def correct_price(payment):
    return payment.mc_gross >= Products[payment.product_type]['price']


def handle_new_payments():
    new_payments = session.query(PayPalPayments) \
        .filter_by(status='new') \
        .order_by(PayPalPayments.payment_id) \
        .all()

    for payment in new_payments:
        now = datetime.utcnow().strftime("%Y-%M-%d %H:%M:%S")
        print "[%s] Processing new payment (id: %s, trx_id: %s) for %s from %s." % (now, payment.payment_id, payment.transaction_id, payment.product_type, payment.payer_email)
        if payment_already_completed(payment):
            print "Payment (id: %s, trx_id: %s) has already been completed." % (payment.payment_id, payment.transaction_id)
            payment.status = 'already_completed'
            session.commit()
            continue

        if payment.product_type not in Products:
            print "Unknown product type %s for payment (id: %s, trx_id: %s)" % (payment.product_type, payment.payment_id, payment.transaction_id)
            payment.status = 'unknown_product'
            session.commit()
            continue

        if not valid_paypal_payment(payment):
            print "Payment (id: %s, trx_id: %s) is invalid." % (payment.payment_id, payment.transaction_id)
            payment.status = 'invalid'
            session.commit()
            continue

        if not completed_paypal_payment(payment):
            print "Payment (id: %s, trx_id: %s) has PayPal status %s (not 'Completed')." % (payment.payment_id, payment.transaction_id, payment.payment_status)
            payment.status = 'not_paypal_completed'
            session.commit()
            continue

        if not correct_price(payment):
            print "Payment (id: %s, trx_id: %s) has wrong price (has: %s, should be: %s)." % (payment.payment_id, payment.transaction_id, payment.mc_gross, Products[payment.product_type]['price'])
            payment.status = 'wrong_price'
            session.commit()
            continue

        Products[payment.product_type]['handler'](payment)
        payment.status = 'completed'
        session.commit()


if __name__ == "__main__":
    while True:
        handle_new_payments()
        session.commit()
        time.sleep(30)

