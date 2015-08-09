__author__ = 'gipmon'
from email.mime.text import MIMEText
import smtplib
import datetime
import json


def send_alert_droplet_down(femail, temail, droplet):
    send_email(femail, temail, "[DIGITAL OCEAN BACKUPS] Port down", "The droplet: " + droplet.name + " is down!")


def send_report(femail, temail, report):
    send_email(femail, temail, "[DIGITAL OCEAN BACKUPS][REPORT][" + str(datetime.datetime.now().day) + "/" + \
               str(datetime.datetime.now().month) + "/" + str(datetime.datetime.now().year) + "]", report)


def send_email(femail, temail, subject, text):
    config_file = open("config.json", "r")
    backup_data = json.load(config_file)

    username = backup_data["username"]
    password = backup_data["password"]
    smtp_url = backup_data["smtp_url"]
    smtp_port = backup_data["smtp_port"]

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
