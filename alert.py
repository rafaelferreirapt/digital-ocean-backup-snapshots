__author__ = 'gipmon'
from email.mime.text import MIMEText
import smtplib
import datetime
from backupdata import *

def send_alert_droplet_down(femail, temail, droplet):
    send_email(femail, temail, "[DIGITAL OCEAN BACKUPS] Port down", "The droplet: "+droplet.name+" is down!")

def send_report(femail, temail, report):
    send_email(femail, temail, "[DIGITAL OCEAN BACKUPS][REPORT]["+str(datetime.datetime.now().day)+"/"+\
               str(datetime.datetime.now().month)+"/"+str(datetime.datetime.now().year)+"]", report)

def send_email(femail, temail, subject, text):
    global username, passoword, smtp_url, smtp_port

    fromaddr = femail
    toaddr = temail

    msg = MIMEText(text)
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject

    server = smtplib.SMTP(smtp_url, smtp_port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(username, password)

    text = msg.as_string()

    server.sendmail(fromaddr, toaddr, text)
    server.quit()