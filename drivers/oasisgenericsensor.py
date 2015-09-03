# -*- coding: utf-8 -*-

from oasisbase import *


class OasisGenericSensor(OasisBase):

    __mapper_args__ = {
        'polymorphic_identity': 'OasisGenericSensor'
    }

    def __init__(self, device_name):
        super(OasisGenericSensor, self).__init__(device_name)

    def processMessage(self, msg):
        '''
            process message
        '''
        self.processTamper(msg)
        self.processSensor(msg)
        self.processBeacon(msg)
        self.processLowBattery(msg)
