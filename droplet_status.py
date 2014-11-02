__author__ = 'gipmon'
from errno import ECONNREFUSED
from functools import partial
from multiprocessing import Pool
import socket

def droplet_down(droplet):
    host = droplet.networks['v4'][0]['ip_address']
    port = 80

    try:
        socket.socket().connect((host, port))
        return True
    except socket.error as err:
        if err.errno == ECONNREFUSED:
            return False
        raise