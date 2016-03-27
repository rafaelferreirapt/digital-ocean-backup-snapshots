import pyocean
import datetime
import time
import socket
import json
from alert import Alert


class Backup:
    def __init__(self, access_token=None):
        self.digital_ocean = access_token
        self.report = ""
        config_file = open("config.json", "r")
        self.backup_data = json.load(config_file)
        self.alert = Alert(self.backup_data["femail"], self.backup_data["temail"])

    def print_snapshots(self, droplet=None):
        if droplet is None:
            return None

        self.report += "[Snapshots for:] " + droplet.name + "\n"

        for snap in droplet.get_snapshots():
            self.report += str(snap) + "\n"

    def snapshot(self, droplet=None):
        if droplet is None:
            return None
        try:
            # if the droplet is active we must power of the droplet and then
            # make the snapshot and then power on again
            if droplet.status == "active":
                try:
                    self.report += "[Power off:] " + droplet.name + "\n"

                    # attempt grateful shutdown
                    droplet.shutdown()

                    # now we must refresh the droplet state
                    droplet = self.digital_ocean.droplet.get(droplet.id)

                    timeout = 0

                    while droplet.status != "off" and timeout < 20:
                        # try to see if is power off
                        droplet = self.digital_ocean.droplet.get(droplet.id)

                        # wait 1 sec
                        time.sleep(1)

                    # now power off
                    droplet.power_off()
                    time.sleep(20)

                    # now we must refresh the droplet state
                    droplet = self.digital_ocean.droplet.get(droplet.id)
                except pyocean.exceptions.DOException as e:
                    if e.code is not 422:
                        self.report += ('ERROR: %s' % e)

            self.report += "[Create snapshot for:] " + droplet.name + "\n"
            droplet.create_snapshot(droplet.name + str(datetime.datetime.now().day) +
                                    str(datetime.datetime.now().month) + str(datetime.datetime.now().year))

            # now we must refresh the droplet state
            droplet = self.digital_ocean.droplet.get(droplet.id)

            # print all the snapshots taken so far
            self.print_snapshots(droplet)
            time.sleep(20)
        except pyocean.exceptions.DOException as e:
            self.report += ('ERROR: %s' % e)

    @staticmethod
    def need_to_backup(droplet=None):
        if droplet is None:
            return False

        # get a list of snapshots
        snaps = [snap for snap in droplet.get_snapshots()]

        # if the last one snapshot has a today date, it don't need to be backup
        if len(snaps) == 0:
            return True

        return snaps[-1].name != (droplet.name + str(datetime.datetime.now().day) + str(datetime.datetime.now().month) +
                                  str(datetime.datetime.now().year))

    def clean_snapshots(self, droplet=None):
        if droplet is None:
            return None

        snaps = [snap for snap in droplet.get_snapshots()]

        if len(snaps) <= self.backup_data["max_snaps"]:
            self.report += "[No need to clean snaps for:] " + droplet.name + "\n"
        else:
            while len(snaps) > self.backup_data["max_snaps"]:
                self.report += "[TASK: Destroying snap:] " + snaps[0].name + "\n"
                snaps[0].destroy()
                self.report += "[DONE: left:] " + str(len(snaps) - (self.backup_data["max_snaps"] + 1)) + "\n"
                # refresh the list
                snaps = [snap for snap in droplet.get_snapshots()]

        return self.report

    def run(self):
        try:
            for account in self.backup_data["accountsList"]:
                self.digital_ocean = pyocean.DigitalOcean(account)

                for droplet in self.digital_ocean.droplet.all():
                    # refresh the state of the digital ocean droplet
                    droplet = self.digital_ocean.droplet.get(droplet.id)

                    # if need to be backup the droplet must be made a snapshot to the droplet
                    if self.need_to_backup(droplet):
                        self.snapshot(droplet)
                        self.clean_snapshots(droplet)
                    else:
                        self.report += "[Snapshot already taken for:] " + droplet.name + "\n"

                    # see if apache is running
                    host = droplet.networks['v4'][0]['ip_address']
                    port = 80

                    try:
                        socket.socket().connect((host, port))
                    except socket.error:
                        self.alert.send_alert_droplet_down(droplet)

                    self.report += "\n"

                # make all droplets active, they must be active
                for droplet in self.digital_ocean.droplet.all():
                    # refresh the state of the digital ocean droplet
                    droplet = self.digital_ocean.droplet.get(droplet.id)

                    if droplet.status == "off":
                        try:
                            droplet.power_on()
                        except pyocean.exceptions.DOException as e:
                            if e.code is 422:
                                continue
                            else:
                                self.report += ('ERROR: %s' % e)

        except pyocean.exceptions.DOException as e:
            self.report += ('ERROR: %s' % e)
        self.alert.send_report(self.report)


if __name__ == "__main__":
    backup = Backup()
    backup.run()
