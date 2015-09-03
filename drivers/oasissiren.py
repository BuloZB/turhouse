# -*- coding: utf-8 -*-

from oasisbase import *


class OasisSiren(OasisBase):

    __mapper_args__ = {
        'polymorphic_identity': 'OasisSiren'
    }

    def __init__(self, device_name):
        super(OasisSiren, self).__init__(device_name)

    def processMessage(self, msg):
        '''
            process message
        '''
        self.processTamper(msg)
        self.processButton(msg)
        self.processBeacon(msg)
        self.processBlackout(msg)

    def processBlackout(self, msgDict):
        """
           process blackout message
        """
        if msgDict['msg'][3] == 'BLACKOUT:1':
            pass
            # TODO
        if msgDict['msg'][3] == 'BLACKOUT:0':
            pass
            # TODO
