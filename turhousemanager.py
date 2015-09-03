# -*- coding: utf-8 -*-

import time
import datetime
import schedule
import logging
from pprint import pprint

from glob import Glob
from alarm.alarmmanager import AlarmManager
from event.notification import ezs_email


class TurhouseManager(AlarmManager):

    '''
      turhouse manager object
    '''

    def __init__(self):
        self._alarm = False
        AlarmManager. __init__(self)

    def beep(self):
        self.device('dongle_1').beep()

    def alarm(self, sender, event_type, params):
        self._alarm = True
        self.device('dongle_1').alarm()
        ezs_email('Alarm: ', sender, event_type, params)

    def alarmStop(self, sender, event_type, params):
        if self._alarm:
            ezs_email('Alarm Stop: ', sender, event_type, params)
        self.device('dongle_1').alarmStop()
        self._alarm = False

    def controllerEventHandler(self, sender, event_type, params):
        Glob.logger.info(
            "Controller %s code: %s " % (sender, params['code']))
        code = params['code']
        if code == 1:
            self.zone('dum').arm()
            self.beep()
        if code == 2:
            self.zone('dum').disarm()
            self.alarmStop(sender, event_type, params)
            self.beep()
        if code == 3:
            self.device('zasuvka_1').toggle()
            self.beep()
