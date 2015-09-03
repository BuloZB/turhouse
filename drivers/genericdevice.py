# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import sqlalchemy
from sqlalchemy import Column, DateTime, Integer, String

from dborm.ormbase import OrmBase
from glob import Glob


class GenericDevice(OrmBase):

    '''
    base class representing all common features of all devices
    & binding to DB
    every device driver has to have functions:
    checkTimeout and processMessage
    '''

    __tablename__ = 'device_status'
    id = Column(Integer, primary_key=True)
    type = Column(String(32))
    device_name = Column(String(32))
    status = Column(String(32), nullable=True)
    status2 = Column(String(32), nullable=True)
    status3 = Column(String(32), nullable=True)
    beacon_timestamp = Column(DateTime, nullable=True)
    sensor_timestamp = Column(DateTime, nullable=True)
    tamper_timestamp = Column(DateTime, nullable=True)
    low_battery_timestamp = Column(DateTime, nullable=True)
    defect_timesatmp = Column(DateTime, nullable=True)
    status_timestamp = Column(DateTime, nullable=True)
    status2_timestamp = Column(DateTime, nullable=True)
    status3_timestamp = Column(DateTime, nullable=True)

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'GenericDevice'
    }

    def __init__(self, device_name):
        self.device_name = device_name
        OrmBase. __init__(self)

    def init(self):
        self.options = {}
        pass

    def setOptions(self, options):
        self.setDefaultOptions()
        if type(options) is dict:
            self.options.update(options)

    def setDefaultOptions(self):
        pass

    def setUnit(self, unit):
        self.unit = unit

    def getStatus(self):
        '''
           get current status value
        '''
        return self.status

    def setGenericStatus(self, statusName, value):
        old = getattr(self, statusName)
        if value != old:
            setattr(self, statusName, value)
            setattr(self, statusName + '_timestamp', sqlalchemy.func.datetime('now', 'localtime'))

    def setStatus(self, value):
        self.setGenericStatus('status', value)

    def getStatus2(self):
        '''
           get current status2 value
        '''
        return self.status2

    def setStatus2(self, value):
        self.setGenericStatus('status2', value)

    def getStatus3(self):
        '''
           get current status3 value
        '''
        return self.status3

    def setStatus3(self, value):
        self.setGenericStatus('status3', value)

    def setTamper(self, value=None):
        if self.tamper_timestamp is None:
            self.tamper_timestamp = sqlalchemy.func.datetime('now', 'localtime')

    def checkTimeout(self):
        pass

    def processMessageSession(self, msgDict):
        session = Glob.dbSession()
        session.add(self)
        self.processMessage(msgDict)
        session.commit()
        session.close()

    def processMessage(self, msgDict):
        '''
            generic function to be rewritten in every device
        '''
        pass

    def sendEvent(self, event_type, params=None):
        '''
            send event to the manager
        '''
        Glob.manager.processEvent(self.device_name, event_type, params)

    def hasSensorEvent(self, interval):
        '''
            return true if there is some sensor evet in last "interval" minutes
        '''
        if self.sensor_timestamp > (datetime.now() - timedelta(minutes=interval)):
            return True
        return False
