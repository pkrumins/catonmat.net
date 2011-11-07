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

from catonmat.models import PayPalPayments, session

PayPalSandbox = False

MailServer = "localhost"
MailFrom = "Peteris Krumins <peter@catonmat.net>"

PayPalUrl = "www.sandbox.paypal.com" if PayPalSandbox else "www.paypal.com"

EmailTemplatePath = "/home/pkrumins/catonmat/payments"
AwkBookPath = "/home/pkrumins/lvm0/Workstation/catonmat/books/awk-one-liners-explained"
SedBookPath = "/home/pkrumins/lvm0/Workstation/catonmat/books/sed-one-liners-explained"
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

    if payment.product_type == 'awk_book':
        bgcontents = "Prepared exclusively for !NAME! !SURNAME! (!EMAIL!)"
    elif payment.product_type == 'awk_book_shantanu':
        bgcontents = "Prepared exclusively for !NAME! !SURNAME! (!EMAIL!) from Shantanu N Kulkarni's Awk class"
    else:
        print "Unknown product_type %s" % payment.product_type

    bgcontents = template_replace(bgcontents, {
        "NAME" : payment.first_name,
        "SURNAME" : payment.last_name,
        "EMAIL" : email
    })

    data = template_replace(data, {
        "NAME" : payment.first_name,
        "SURNAME" : payment.last_name,
        "EMAIL" : email,
        "BGCONTENTS" : bgcontents
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

    print "Sending the Awk book to %s %s (%s)." % (unidecode(payment.first_name), unidecode(payment.last_name), payment.payer_email)
    send_mail(payment.payer_email, MailFrom, Products['awk_book']['subject'], email_body, attachment, attachment_name)

def sed_book_template(infile, outfile, payment):
    fd = open("%s/%s" % (SedBookPath, infile))
    data = fd.read()
    fd.close()

    email = payment.payer_email.replace("_", "\\_")

    data = template_replace(data, {
        "NAME" : payment.first_name,
        "SURNAME" : payment.last_name,
        "EMAIL" : email
    })

    fd = open("%s/%s" % (SedBookPath, outfile), 'w+')
    fd.write(data.encode('utf-8'))
    fd.close()

def sed_book(payment):
    print "Preparing Sed Book..."
    subject = Products['sed_book']['subject']
    attachment = "%s/%s" % (SedBookPath, Products['sed_book']['file'])
    attachment_name = Products['sed_book']['attachment_name']
    
    fd = open(EmailTemplatePath + '/thanks-sed-book.txt')
    body = fd.read()
    fd.close()

    email_body = template_replace(body, {
        "NAME": payment.first_name,
        "SURNAME": payment.last_name
    })

    sed_book_template('sedbook_template.tex', 'sedbook.tex', payment)
    sed_book_template('chapter1_template.tex', 'chapter1.tex', payment)
    sed_book_template('chapter4_template.tex', 'chapter4.tex', payment)
    sed_book_template('chapter6_template.tex', 'chapter6.tex', payment)

    print "Spawning Latex..."
    latex_log = open(LatexLogPath, 'a+')
    latex = subprocess.Popen("pdflatex sedbook.tex", stdout=latex_log, stderr=latex_log, cwd=SedBookPath, shell=True)
    latex.wait()

    print "Spawning makeindex..."
    makeindex = subprocess.Popen("makeindex sedbook", stdout=latex_log, stderr=latex_log, cwd=SedBookPath, shell=True)
    makeindex.wait()

    print "Spawning Latex 2nd time..."
    latex = subprocess.Popen("pdflatex sedbook.tex", stdout=latex_log, stderr=latex_log, cwd=SedBookPath, shell=True)
    latex.wait()

    print "Spawning Latex 3nd time..."
    latex = subprocess.Popen("pdflatex sedbook.tex", stdout=latex_log, stderr=latex_log, cwd=SedBookPath, shell=True)
    latex.wait()
    latex_log.close()

    print "Sending the Sed book to %s %s (%s)." % (unidecode(payment.first_name), unidecode(payment.last_name), payment.payer_email)
    send_mail(payment.payer_email, MailFrom, Products['sed_book']['subject'], email_body, attachment, attachment_name)


Products = {
    'awk_book': {
        'subject' : 'Your Awk One-Liners Explained E-Book!',
        'file' : 'awkbook.pdf',
        'attachment_name' : 'awk-one-liners-explained.pdf',
        'price' : '5.95',
        'email_body' : 'thanks-awk-book.txt',
        'handler' : awk_book
    },
    'awk_book_995': {
        'subject' : 'Your Awk One-Liners Explained E-Book!',
        'file' : 'awkbook.pdf',
        'attachment_name' : 'awk-one-liners-explained.pdf',
        'price' : '9.95',
        'email_body' : 'thanks-awk-book.txt',
        'handler' : awk_book
    },
    'awk_book_shantanu' : {
        'subject' : 'Your Awk One-Liners Explained E-Book!',
        'file' : 'awkbook.pdf',
        'attachment_name' : 'awk-one-liners-explained.pdf',
        'price' : '2.50',
        'email_body' : 'thanks-awk-book.txt',
        'handler' : awk_book
    },
    'sed_book': {
        'subject' : 'Your Sed One-Liners Explained E-Book!',
        'file' : 'sedbook.pdf',
        'attachment_name' : 'sed-one-liners-explained.pdf',
        'price' : '9.95',
        'email_body' : 'thanks-sed-book.txt',
        'handler' : sed_book
    },
    'sed_book_shantanu': {
        'subject' : 'Your Sed One-Liners Explained E-Book!',
        'file' : 'sedbook.pdf',
        'attachment_name' : 'sed-one-liners-explained.pdf',
        'price' : '2.50',
        'email_body' : 'thanks-sed-book.txt',
        'handler' : sed_book
    },
}


def send_mail(mail_to, mail_from, subject, body, attachment, attachment_name):
    TO = [mail_to]

    mail = MIMEMultipart()
    mail['Subject'] = subject
    mail['From'] = mail_from
    mail['To'] = ','.join(TO)

    mailbody = MIMEText(body.encode('utf8'), 'plain')
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
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
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


def handle_free_payments():
    new_payments = session.query(PayPalPayments) \
        .filter_by(status='free') \
        .order_by(PayPalPayments.payment_id) \
        .all()

    for payment in new_payments:
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        print "[%s] Processing free payment (id: %s, trx_id: %s) for %s from %s." % (now, payment.payment_id, payment.transaction_id, payment.product_type, payment.payer_email)
        Products[payment.product_type]['handler'](payment)
        payment.status = 'completed_free'
        session.commit()


if __name__ == "__main__":
    while True:
        handle_new_payments()
        handle_free_payments()
        session.commit()
        time.sleep(30)

