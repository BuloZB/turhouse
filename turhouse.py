#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import getopt
import logging
import logging.config

from glob import *
import turhouseconfig
import turhousemanager
from dborm import turhousedb

import pdb

'''
    main turhouse program
'''


def createDaemon(daemonClass):
    """
        create dongle listener daemon
    """

    try:
        pid = os.fork()

        if pid > 0:
            # parent
            Glob.logger.info('daemon: %s, pid: %s' % (daemonClass, pid))
            return pid

    except OSError, error:
        print 'Unable to fork. Error: %d (%s)' % (error.errno, error.strerror)
        os._exit(1)

    # child
    module = __import__(daemonClass.lower())
    class_ = getattr(module, daemonClass)
    instance = class_()
    instance.main()


def main(argv):
    '''
        main function
    '''

    # init
    configfile = ''
    dumpconf = False

    try:
        opts, args = getopt.getopt(
            argv, "hdc:", ["help", "debug", "config=", "dumpconf"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in("-d", "--debug"):
            global _debug
            _debug = 1
        elif opt in("--dumpconf",):
            dumpconf = 1
        elif opt in ("-c", "--config"):
            configfile = arg

    # load turhouse config
    Glob.config = turhouseconfig.TurhouseConfig(configfile)
    if dumpconf:
        Glob.config.createDump()
        os._exit(0)

    # load logging config
    try:
        logging.config.fileConfig(Glob.config.loggingConf())
    except Exception as e:
        print "Unable to init logging %s" % str(e)

    Glob.logger = logging.getLogger('main')
    Glob.logger.info("Turhouse start")

    Glob.devices = DevicePool()
    Glob.zones = ZonePool()

    turhousedb.dbConnect()
    Glob.manager = turhousemanager.TurhouseManager()

    # start daemons
    daemons = Glob.config.daemons()
    for daemonClass in daemons:
        createDaemon(daemonClass)


def usage():
    print(
        "Usage: turhouse.py [--help] [--debug] [--config=<file>] [--dumpconf]")

if __name__ == '__main__':
    main(sys.argv[1:])
