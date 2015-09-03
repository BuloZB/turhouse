# -*- coding: utf-8 -*-

from genericcontroller import *
from oasisbase import *


class OasisController86K(OasisBase, GenericController):

    __mapper_args__ = {
        'polymorphic_identity': 'OasisController86K'
    }

    def __init__(self, device_name):
        OasisBase.__init__(self, device_name)
        GenericController.__init__(self, device_name)

    def setDefaultOptions(self):
        OasisBase.setDefaultOptions(self)
        GenericController.setDefaultOptions(self)
        self.options.update({'beep': 1})

    def processMessage(self, msgDict):
        '''
            process message
        '''
        self.keyPressed(self.getKey(msgDict))
        self.processLowBattery(msgDict)

    def getKey(self, msgDict):
        '''
            return pressed key number
            left lock = 1, left ulock = 2, right lock = 3, right unlock = 4, left PANIC = 5, right PANIC = 6
        '''
        msg = msgDict['msg']
        if msg[2] == 'ARM:1':
            key = 1
            key2 = 3
        elif msg[2] == 'ARM:0':
            key = 2
            key2 = 4
        elif msg[2] == 'PANIC':
            key = 5
            key2 = 6
        else:
            logger.error('Unknown controller event %s' % msg[2])
            pass
        id_ = msgDict['id']
        if (id_ & (1 << 20)):
            key = key2
        return key

    def sendSequence(self):
        '''
            create new event with current sequence
        '''
        GenericController.sendSequence(self)
