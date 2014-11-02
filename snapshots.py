__author__ = 'gipmon'
import sys
import pyocean
import datetime
import alert
import droplet_status

ACCESS_TOKEN1 = "YOUR_ACCESS_TOKEN"
ACCESS_TOKEN2 = "YOUR_ACCESS_TOKEN"
accountsList = [pyocean.DigitalOcean(ACCESS_TOKEN1), pyocean.DigitalOcean(ACCESS_TOKEN2)]
digitalocean = accountsList[0] #init digitalocean

max_snaps = 15
femail = "EMAIL"
temail = "EMAIL"

report = ""

def printAllSnapshots():
    global report
    try:
        for droplet in digitalocean.droplet.all():
            report += printSnapshots(droplet)
    except pyocean.exceptions.DOException as e:
        report = ('ERROR: %s\n' % e)

def printSnapshots(droplet = None):
    global report
    if droplet == None:
        return None
    report += "[Snapshots for:] " + droplet.name + "\n"
    snaps = droplet.get_snapshots()
    for snap in snaps:
        report += snap + "\n"

def snapshot(droplet = None):
    global report
    if droplet == None:
        return None
    try:
        report += "[Power off:] " + droplet.name + "\n"
        droplet.power_off()

        report += "[Create snapshot for:] " + droplet.name + "\n"
        droplet.create_snapshot(droplet.name + str(datetime.datetime.now().day) + str(datetime.datetime.now().month)\
                                + str(datetime.datetime.now().year))

        printSnapshots(droplet)
    except pyocean.exceptions.DOException as e:
        report += ('ERROR: %s' % e)

def snapsToList(snapshots = None):
    if snapshots == None:
        return None
    return [snap for snap in snapshots]

def hasSnap(droplet = None):
    if droplet == None:
        return None
    snaps = snapsToList(droplet.get_snapshots())
    return snaps[-1].name == (droplet.name + str(datetime.datetime.now().day) + str(datetime.datetime.now().month)\
                              + str(datetime.datetime.now().year))

def cleanSnapshots(droplet = None):
    global report
    if droplet == None:
        return None
    snaps = snapsToList(droplet.get_snapshots())
    if len(snaps) <= max_snaps:
        report += "[No need to clean snaps for:] " + droplet.name + "\n"
    else:
        while len(snaps) > max_snaps:
            report += "[TASK: Destroying snap:] " + snaps[0].name + "\n"
            snaps[0].destroy()
            report += "[DONE: left:] " + str(len(snaps)-(max_snaps+1)) + "\n"
            snaps = snapsToList(droplet.get_snapshots())
    return report

if __name__=="__main__":
    try:
        for accout in accountsList:
            digitalocean = accout
            for droplet in digitalocean.droplet.all():
                if hasSnap(droplet) == False:
                    snapshot(droplet)
                else:
                    report += "[Snapshot already taken for:] " + droplet.name + "\n"
                if not droplet_status.droplet_down(droplet):
                    alert.send_alert_droplet_down(femail, temail, droplet)
                cleanSnapshots(droplet)
    except pyocean.exceptions.DOException as e:
        report += ('ERROR: %s' % e)
    alert.send_report(femail, temail, report)