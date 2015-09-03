import smtplib

from glob import Glob
import smtplib


def ezs_email(msg_type, sender, event_type, params):

    cfg = Glob.config.notification()
    fromaddr = cfg['from_email']
    toaddr = cfg['alarm_notify_emails']

    message = """\
From: %s
To: %s
Subject: %s %s %s %s

...

""" % (fromaddr, fromaddr, msg_type, sender, event_type, params)
    email(fromaddr, toaddr, message)


def email(fromaddr, toaddr, message):
    cfg = Glob.config.smtp()

    server = smtplib.SMTP(cfg['server'], cfg['port'])
    server.ehlo()
    if cfg['tls']:
        server.starttls()
        server.ehlo()
    server.login(cfg['username'], cfg['password'])
    server.sendmail(fromaddr, ", ".join(toaddr), message)
    server.quit()
