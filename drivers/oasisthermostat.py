# -*- coding: utf-8 -*-

from oasisbase import *

import re


class OasisThermostat(OasisBase):

    __mapper_args__ = {
        'polymorphic_identity': 'OasisThermostat'
    }

    def __init__(self, device_name):
        super(OasisThermostat, self).__init__(device_name)

    def processMessage(self, msg):
        '''
            process message
        '''
        self.processTemperature(msg)
        self.processBeacon(msg)
        self.processLowBattery(msg)

    def processTemperature(self, msgDict):
        '''
           process message of thermometer
        '''
        statusMsg = msgDict['msg'][2]
        m = re.search("^(INT|SET):(....)", statusMsg)
        if m:
            temptype, temp = m.groups()
            if temptype == 'INT':
                self.setStatus(temp)
            else:
                self.setStatus2(temp)
