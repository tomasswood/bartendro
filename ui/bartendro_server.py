#!/usr/bin/env python

from bartendro import app
import logging
import os
import memcache
import sys
import uwsgi
from bartendro.router import driver
from bartendro import mixer
from bartendro.errors import SerialIOError, I2CIOError

class BartendroLock(object):

    def lock_bartendro(self):
        """Call this function before making a drink or doing anything that where two users' action may conflict.
           This function will return True if the lock was granted, of False is someone else has already locked 
           Bartendro."""

        uwsgi.lock()
        is_locked = uwsgi.sharedarea_readbyte(0)
        if is_locked:
           uwsgi.unlock()
           return False
        uwsgi.sharedarea_writebyte(0, 1)
        uwsgi.unlock()

        return True

    def unlock_bartendro(self):
        """Call this function when you've previously locked bartendro and now you want to unlock it."""

        uwsgi.lock()
        is_locked = uwsgi.sharedarea_readbyte(0)
        if not is_locked:
           uwsgi.unlock()
           return False
        uwsgi.sharedarea_writebyte(0, 0)
        uwsgi.unlock()

        return True

def print_software_only_notice():
    print """If you're trying to run this code without having Bartendro hardware,
you can still run the software portion of it in a simulation mode. In this mode no 
communication with the Bartendro hardware will happen to allow the software to run.
To enable this mode, set the BARTENDRO_SOFTWARE_ONLY environment variable to 1 and 
try again:

    > export BARTENDRO_SOFTWARE_ONLY=1

"""

try:
    import config
except ImportError:
    print "You need to create a configuration file called config.py by copying"
    print "config.py.default to config.py . Edit the configuration options in that"
    print "file to tune bartendro to your needs, then start the server again."
    sys.exit(-1)
app.options = config

if len(sys.argv) > 1 and sys.argv[1] == "--debug":
    debug = True
else:
    debug = False

# For now, leave debug on
debug = True

try: 
    app.software_only = 1 #int(os.environ['BARTENDRO_SOFTWARE_ONLY'])
    app.num_dispensers = 15
except KeyError:
    app.software_only = 0

if not os.path.exists("bartendro.db"):
    print "bartendro.db file not found. Please copy bartendro.db.default to "
    print "bartendro.db in order to provide Bartendro with a starting database."
    sys.exit(-1)

# Create a memcache connection and flush everything
app.mc = memcache.Client(['127.0.0.1:11211'], debug=0)
app.mc.flush_all()

app.lock = BartendroLock()

app.log = logging.getLogger('bartendro')
try:
    app.driver = driver.RouterDriver("/dev/ttyAMA0", app.software_only);
    app.driver.open()
except I2CIOError:
    print
    print "Cannot open I2C interface to a router board."
    print
    print_software_only_notice()
    sys.exit(-1)
except SerialIOError:
    print
    print "Cannot open serial interface to a router board."
    print
    print_software_only_notice()
    sys.exit(-1)

app.log.info("Found %d dispensers." % app.driver.count())

app.mixer = mixer.Mixer(app.driver, app.mc)

if app.software_only:
    app.log.info("Running SOFTWARE ONLY VERSION. No communication between software and hardware chain will happen!")

app.log.info("Bartendro starting")

app.debug = debug

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8091)
