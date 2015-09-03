# -*- coding: utf-8 -*-

from oasisbase import *


class OasisRelay(OasisBase):

    __mapper_args__ = {
        'polymorphic_identity': 'OasisRelay'
    }

    def __init__(self, device_name):
        super(OasisRelay, self).__init__(device_name)

    def getStatus(self):
        '''
           get current status value
        '''
        if self.status is None:
            return '0'
        return self.status

    def processMessage(self, msg):
        '''
            process message
        '''
        self.processRelayMessage(msg)

    def processRelayMessage(self, msgDict):
        '''
            process relay message
        '''
        statusMsg = msgDict['msg'][2]
        if statusMsg == 'RELAY:1':
            self.setStatus(1)
        elif statusMsg == 'RELAY:0':
            self.setStatus(0)
        else:
            Glob.logger.error('unknown relay status %s' % statusMsg)

    def sendStatus(self, val):
        '''
            set value to new state and notify device about change
        '''
        session = Glob.dbSession()
        self.setStatus(val)
        session.add(self)
        session.commit()
        session.close()
        self.unit.sendStatus()

    def on(self):
        '''
            switch the relay on
        '''
        self.sendStatus(1)

    def off(self):
        '''
            switch the relay on
        '''
        self.sendStatus(0)

    def toggle(self):
        '''
            toggle the relay
        '''
        self.sendStatus(1 - int(self.getStatus()))
