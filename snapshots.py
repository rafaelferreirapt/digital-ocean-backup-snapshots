import pyocean
import datetime
import alert
import droplet_status
import time
import json


class Backup:
    def __init__(self, access_token=None):
        self.digital_ocean = access_token
        self.report = ""
        config_file = open("config.json", "r")
        self.backup_data = json.load(config_file)

    def print_all_snapshots(self):
        try:
            for droplet in self.digital_ocean.droplet.all():
                self.report += self.print_snapshots(droplet)
        except pyocean.exceptions.DOException as e:
            self.report = ('ERROR: %s\n' % e)

    def print_snapshots(self, droplet=None):
        if droplet is None:
            return None

        self.report += "[Snapshots for:] " + droplet.name + "\n"
        snaps = droplet.get_snapshots()

        for snap in snaps:
            self.report += str(snap) + "\n"

    def snapshot(self, droplet=None):
        if droplet is None:
            return None
        try:
            self.report += "[Power off:] " + droplet.name + "\n"

            try:
                droplet.power_off()
                time.sleep(60)
            except pyocean.exceptions.DOException as e:
                if e.code is not 422:
                    self.report += ('ERROR: %s' % e)

            time.sleep(60)

            self.report += "[Create snapshot for:] " + droplet.name + "\n"
            droplet.create_snapshot(droplet.name + str(datetime.datetime.now().day) +
                                    str(datetime.datetime.now().month) + str(datetime.datetime.now().year))

            self.print_snapshots(droplet)
        except pyocean.exceptions.DOException as e:
            self.report += ('ERROR: %s' % e)

    @staticmethod
    def snaps_to_list(snap=None):
        if snap is None:
            return None
        return [snap for snap in snap]

    @staticmethod
    def has_snap(droplet=None):
        if droplet is None:
            return None

        snaps = Backup.snaps_to_list(droplet.get_snapshots())

        return snaps[-1].name == (droplet.name + str(datetime.datetime.now().day) + str(datetime.datetime.now().month) +
                                  str(datetime.datetime.now().year))

    def clean_snapshots(self, droplet=None):
        if droplet is None:
            return None
        snaps = self.snaps_to_list(droplet.get_snapshots())

        if len(snaps) <= self.backup_data["max_snaps"]:
            self.report += "[No need to clean snaps for:] " + droplet.name + "\n"
        else:
            while len(snaps) > self.backup_data["max_snaps"]:
                self.report += "[TASK: Destroying snap:] " + snaps[0].name + "\n"
                snaps[0].destroy()
                self.report += "[DONE: left:] " + str(len(snaps) - (self.backup_data["max_snaps"] + 1)) + "\n"
                snaps = self.snaps_to_list(droplet.get_snapshots())

        return self.report

    def run(self):
        try:
            for account in self.backup_data["accountsList"]:
                self.digital_ocean = pyocean.DigitalOcean(account)
                
                for droplet in backup.digital_ocean.droplet.all():
                    if droplet.status == "off":
                        try:
                            droplet.power_on()
                            time.sleep(60)
                        except pyocean.exceptions.DOException as e:
                            if e.code is 422:
                                continue
                            else:
                                self.report += ('ERROR: %s' % e)

                    if self.has_snap(droplet) is False:
                        backup.snapshot(droplet)
                        time.sleep(60)
                    else:
                        self.report += "[Snapshot already taken for:] " + droplet.name + "\n"

                    # see if apache is running
                    if not droplet_status.droplet_down(droplet):
                        alert.send_alert_droplet_down(self.backup_data["femail"], self.backup_data["temail"], droplet)

                    self.clean_snapshots(droplet)
                    self.report += "\n"

                # make all droplets active
                for droplet in backup.digital_ocean.droplet.all():
                    if droplet.status == "off":
                        try:
                            droplet.power_on()
                            time.sleep(60)
                        except pyocean.exceptions.DOException as e:
                            if e.code is 422:
                                continue
                            else:
                                self.report += ('ERROR: %s' % e)

        except pyocean.exceptions.DOException as e:
            self.report += ('ERROR: %s' % e)
        alert.send_report(self.backup_data["femail"], self.backup_data["temail"], self.report)


if __name__ == "__main__":
    backup = Backup()
    backup.run()
