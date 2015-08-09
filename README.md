Backup your droplets with snapshots
==============================

With this python script you can backup your droplets in different accounts every day (cronjob) and the script will send
to you a report or a alert when the droplet is down after the backup. All the alerts are send via email.

#### Requirements
Python wrapper for DigitalOcean: [PyOcean](https://github.com/bsdnoobz/pyocean/)

Install:
sudo pip install digitalocean-python

#### Usage
### Fill the data in config.json

ACCESS_TOKEN1 = "YOUR_ACCESS_TOKEN" #other account

ACCESS_TOKEN2 = "YOUR_ACCESS_TOKEN" #other account

max_snaps = NUMBER # max snapshots for droplet stored

femail = "EMAIL" #from email for the alert messages

temail = "EMAIL" # to email for the alert messages

username = "EMAIL" #username for the SMTP server

password = "PASSWORD" # password

smtp_url = "SMTP_URL" # url of the SMTP server

smtp_port = 587 # PORT NUMBER
