__author__ = 'gipmon'
import sys
import pyocean
import datetime
import alert
import droplet_status
from backupdata import *

report = ""

class Backup():
    def __init__(self, access_token=None):
        self.digitalocean = access_token

    def printAllSnapshots(self):
        global report
        try:
            for droplet in self.digitalocean.droplet.all():
                report += self.printSnapshots(droplet)
        except pyocean.exceptions.DOException as e:
            report = ('ERROR: %s\n' % e)

    def printSnapshots(self, droplet = None):
        global report
        if droplet == None:
            return None
        report += "[Snapshots for:] " + droplet.name + "\n"
        snaps = droplet.get_snapshots()
        for snap in snaps:
            report += str(snap) + "\n"

    def snapshot(self, droplet = None):
        global report
        if droplet == None:
            return None
        try:
            report += "[Power off:] " + droplet.name + "\n"
            droplet.power_off()

            report += "[Create snapshot for:] " + droplet.name + "\n"
            droplet.create_snapshot(droplet.name + str(datetime.datetime.now().day) + str(datetime.datetime.now().month)\
                                    + str(datetime.datetime.now().year))

            self.printSnapshots(droplet)
        except pyocean.exceptions.DOException as e:
            report += ('ERROR: %s' % e)

    def snapsToList(self, snapshots = None):
        if snapshots == None:
            return None
        return [snap for snap in snapshots]

    def hasSnap(self, droplet = None):
        if droplet == None:
            return None
        snaps = self.snapsToList(droplet.get_snapshots())
        return snaps[-1].name == (droplet.name + str(datetime.datetime.now().day) + str(datetime.datetime.now().month)\
                                  + str(datetime.datetime.now().year))

    def cleanSnapshots(self, droplet = None):
        global report
        if droplet == None:
            return None
        snaps = self.snapsToList(droplet.get_snapshots())
        if len(snaps) <= max_snaps:
            report += "[No need to clean snaps for:] " + droplet.name + "\n"
        else:
            while len(snaps) > max_snaps:
                report += "[TASK: Destroying snap:] " + snaps[0].name + "\n"
                snaps[0].destroy()
                report += "[DONE: left:] " + str(len(snaps)-(max_snaps+1)) + "\n"
                snaps = self.snapsToList(droplet.get_snapshots())
        return report

if __name__=="__main__":
    backup = Backup()
    try:
        for accout in accountsList:
            backup.digitalocean = pyocean.DigitalOcean(accout)
            for droplet in backup.digitalocean.droplet.all():
                if backup.hasSnap(droplet) == False:
                    backup.snapshot(droplet)
                else:
                    report += "[Snapshot already taken for:] " + droplet.name + "\n"
                if not droplet_status.droplet_down(droplet):
                    alert.send_alert_droplet_down(femail, temail, droplet)
                backup.cleanSnapshots(droplet)
                report += "\n"
    except pyocean.exceptions.DOException as e:
        report += ('ERROR: %s' % e)
    alert.send_report(femail, temail, report)