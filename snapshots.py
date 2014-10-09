__author__ = 'gipmon'
import sys
import pyocean
import datetime

ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
digitalocean = pyocean.DigitalOcean(ACCESS_TOKEN)
now = datetime.datetime.now()
max_snaps = 5

def printAllSnapshots():
    try:
        for droplet in digitalocean.droplet.all():
            printSnapshots(droplet)
            print ""
    except pyocean.exceptions.DOException as e:
        print('ERROR: %s' % e)

def printSnapshots(droplet = None):
    if droplet == None:
        return None
    print "[Snapshots for:] " + droplet.name
    snaps = droplet.get_snapshots()
    for snap in snaps:
        print snap

def snapshot(droplet = None):
    if droplet == None:
        return None
    try:
        print "[Power off:] " + droplet.name
        droplet.power_off()

        print "[Create snapshot for:] " + droplet.name
        droplet.create_snapshot(droplet.name + str(now.day) + str(now.month) + str(now.year))

        printSnapshots(droplet)
        print ""
    except pyocean.exceptions.DOException as e:
        print('ERROR: %s' % e)

def snapsToList(snapshots = None):
    if snapshots == None:
        return None
    return [snap for snap in snapshots]

def hasSnap(droplet = None):
    if droplet == None:
        return None
    snaps = snapsToList(droplet.get_snapshots())
    return snaps[-1].name == (droplet.name + str(now.day) + str(now.month) + str(now.year))

def cleanSnapshots(droplet = None):
    if droplet == None:
        return None
    snaps = snapsToList(droplet.get_snapshots())
    if len(snaps) <= max_snaps:
        print "[No need to clean snaps for:] " + droplet.name
    else:
        while len(snaps = snapsToList(droplet.get_snapshots())) > 5:
            print "[TASK: Destroying snap:] " + snaps.name
            snaps[0].destroy()
            print "[DONE: left:] " + str(len(snaps)-6)

if __name__=="__main__":
    try:
        for droplet in digitalocean.droplet.all():
            if hasSnap(droplet) == False:
                snapshot(droplet)
            else:
                print "[Snapshot already taken for:] " + droplet.name
            cleanSnapshots(droplet)
    except pyocean.exceptions.DOException as e:
        print('ERROR: %s' % e)