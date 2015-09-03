# -*- coding: utf-8 -*-

import sqlalchemy

from genericdevice import *


class OasisBase(GenericDevice):

    __mapper_args__ = {
        'polymorphic_identity': 'OasisBase'
    }

    def __init__(self, device_name):
        GenericDevice.__init__(self, device_name)

    def processMessage(self, msgDict):
        '''
           process message
        '''
        self.processLowBattery(msgDict)
        self.processBeacon(msgDict)

    def getLoopStatus(self, msgDict):
        """
            return loop status (0,1)
        """
        try:
            status = msgDict['msg'][4]
        except IndexError:
            # pir has no ststus
            return 0
        if status == 'ACT:1':
            r = 1
        elif status == 'ACT:0':
            r = 0
        else:
            logger.error('unknown loop status %s' % status)
        return r

    def processSensor(self, msgDict):
        """
            proces SENSOR event
        """
        if msgDict['msg'][2] == 'SENSOR':
            status = self.getLoopStatus(msgDict)
            self.setStatus(status)
            self.sensor_timestamp = sqlalchemy.func.datetime('now', 'localtime')
            self.sendEvent('Sensor', {'status': status})

    def processTamper(self, msgDict):
        """
            proces TAMPER event
        """
        if msgDict['msg'][2] == 'TAMPER':
            self.setTamper()
            self.sendEvent('Tamper', {'status': self.getLoopStatus(msgDict)})

    def processButton(self, msgDict):
        """
            proces BUTTON event
        """
        if msgDict['msg'][2] == 'BUTTON':
            self.sendEvent('Button')

    def processDefect(self, msgDict):
        """
            proces DEFECT event
        """
        if msgDict['msg'][2] == 'DEFECT' and self.defect_timestamp is None:
            self.defect_timestamp = sqlalchemy.func.datetime('now', 'localtime')
            self.setStatus(self.getLoopStatus(msgDict))

    def processBeacon(self, msgDict):
        """
           store beacon time into db
        """
        self.beacon_timestamp = sqlalchemy.func.datetime('now', 'localtime')
        self.sendEvent('Beacon')

    def processLowBattery(self, msgDict):
        """
           store low_battery_status into db
        """
        if msgDict['msg'][3] == 'LB:1' and self.low_battery_timestamp is None:
            self.low_battery_timestamp = sqlalchemy.func.datetime('now', 'localtime')
        if msgDict['msg'][3] == 'LB:0' and self.low_battery_timestamp:
            self.low_battery_timestamp = None
