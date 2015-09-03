# -*- coding: utf-8 -*-

import time
import datetime
import logging

from pprint import pprint

from device import Device
from glob import Glob


class OasisUnit(object):

    '''
        class representing one oasis unit (turris dongle)
    '''

    def __init__(self, unitName):
        '''
            init
        '''
        self.unitName = unitName
        self.queue = list()
        # pgx device
        self.pgx = None
        # pgy device
        self.pgy = None
        # beeper status
        self.beeper = 'NONE'
        self.device = None
        self.reader = None

        unitDevice = Glob.config.getUnitParams(unitName)['device']
        try:
            self.device = Device(device=unitDevice)
            self.reader = self.device.gen_lines(0.05)
        except Exception as e:
            Glob.logger.error(
                'Unable to open device %s (unit: %s): %s' % (unitDevice, unitName, str(e)))

    def alarm(self):
        self.beeper = 'ALARM'
        self.sendStatus()

    def beepSlow(self):
        self.beeper = 'SLOW'
        self.sendStatus()

    def beepFast(self):
        self.beeper = 'FAST'
        self.sendStatus()

    def alarmStop(self):
        self.beeper = 'NONE'
        self.sendStatus()

    def sendStatus(self, repeat=1, delay=0):
        pgx = 0
        pgy = 0
        if self.pgx:
            pgx = self.pgx.getStatus()
        if self.pgy:
            pgy = self.pgy.getStatus()
        if self.beeper == 'ALARM':
            alarm = 1
            beep = 'NONE'
        else:
            alarm = 0
            beep = self.beeper
        cmd = 'TX ENROLL:0 PGX:%s PGY:%s ALARM:%s BEEP:%s' % (
            pgx, pgy, alarm, beep)
        timestamp = time.time() + delay
        while True:
            self.queueCommand(cmd, timestamp)
            timestamp += 0.2
            repeat -= 1
            if repeat <= 0:
                break

    def queueCommand(self, cmd, timestamp):
        self.queue.append((cmd, timestamp))

    def sendCommand(self, cmd):
        Glob.loggerOasis.info(cmd)
        self.device.send_command(cmd)
        resp = self.reader.next()
        Glob.loggerOasis.info(resp)

    def beep(self):
        st = self.beeper
        self.beeper = 'SLOW'
        self.sendStatus(0)
        self.beeper = st
        self.sendStatus(1, 0.4)

    def checkTimeout(self):
        '''
            check if there is some timeouted command in the queue
        '''
        if self.queue:
            cmd, timestamp = self.queue[0]
            if timestamp < time.time():
                self.sendCommand(cmd)
                self.queue.pop(0)
