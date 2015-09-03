# -*- coding: utf-8 -*-

from oasisbase import *


class OasisSmokeSensor(OasisBase):

    __mapper_args__ = {
        'polymorphic_identity': 'OasisSmokeSensor'
    }

    def __init__(self, device_name):
        super(OasisSmokeSensor, self).__init__(device_name)

    def processMessage(self, msg):
        '''
            process message
        '''
        self.processTamper(msg)
        self.processSensor(msg)
        self.processButton(msg)
        self.processDefect(msg)
        self.processBeacon(msg)
        self.processLowBattery(msg)
