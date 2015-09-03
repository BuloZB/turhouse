# -*- coding: utf-8 -*-

from genericdevice import *

import time


class GenericController(GenericDevice):

    '''
        base controller class implementing seqences of pressed keys
    '''

    __mapper_args__ = {
        'polymorphic_identity': 'GenericController'
    }

    def __init__(self, device_name):
        super(GenericController, self).__init__(device_name)

    def init(self):
        GenericDevice.init(self)
        self.sequence = []
        self.lastTime = None

    def setDefaultOptions(self):
        GenericDevice.setDefaultOptions(self)
        self.options.update({'timeout': 2, 'sequenceLimit': 3})

    def checkTimeout(self):
        '''
            check if there is some timeouted sequence
        '''
        if self.sequence and time.time() - self.lastTime > self.options['timeout']:
            self.sendSequence()

    def keyPressed(self, key):
        '''
           handle the pressed button of the controller
        '''
        self.sequence.append(key)
        if len(self.sequence) >= self.options['sequenceLimit']:
            self.sendSequence()
        else:
            self.lastTime = time.time()

    def sendSequence(self):
        '''
            create new event with current sequence
        '''
        ccode = int(''.join(map(str, self.sequence)))
        self.sequence = []
        # send event
        self.sendEvent('Controller', {'code': ccode})
