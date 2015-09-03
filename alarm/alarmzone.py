# -*- coding: utf-8 -*-

import sqlalchemy
from sqlalchemy import Column, DateTime, Integer, String

from dborm.ormbase import OrmBase
from glob import Glob


class AlarmZone(OrmBase):

    '''
    class representing alarm zone
    & binding to DB
    '''

    __tablename__ = 'alarm_zone'
    id = Column(Integer, primary_key=True)
    zone_name = Column(String(32))
    status = Column(String(32), nullable=True)
    status_timestamp = Column(DateTime, nullable=True)

    def __init__(self, zone_name, status='ready', options=None):
        self.zone_name = zone_name
        self.zoneName = zone_name
        self.status = status
        self.options = {}
        if options is not None:
            self.options.update(options)
        OrmBase. __init__(self)

    def init(self):
        # internal list of devices
        self._devices = set()
        # explored means devices includes all devices from subzones
        self._explored = None
        self._subzones = set()

    def getStatus(self):
        '''
           get current status value
        '''
        return self.status

    def setStatus(self, value):
        '''
            set status & update status_timestamp
        '''
        if value != self.status:
            self.status = value
            self.status_timestamp = sqlalchemy.func.datetime(
                'now', 'localtime')

    def addSubzone(self, subzone):
        '''
            add subzone to the zone
        '''
        self._subzones.add(subzone)

    def addDevice(self, device):
        '''
            add device to the zone
        '''
        self._devices.add(device)

    def getDevices(self):
        '''
            return list of devices which belogngs to the zone (_self.devices)
        '''
        if self._explored is None:
            self.exploreDevices()
        return self._devices

    def exploreDevices(self):
        '''
            init content of self._devices (list of devices which belogngs to the zone)
        '''
        exploredSubzones = set()
        for subzone in self._subzones:
            if subzone not in exploredSubzones:
                self._devices.update(Glob.zones.getZone(subzone).getDevices())
                exploredSubzones.update(subzone)
        self._explored = True
        return self._devices

    def hasDevice(self, deviceName):
        '''
            return true if deviceName is in zone
        '''
        return deviceName in self.getDevices()

    def isArmed(self, status='armed'):
        return self.status == status

    def setStatusRecursively(self, status='armed'):
        session = Glob.dbSession()
        self.setStatus(status)
        exploredSubzones = set()
        for subzone in self._subzones:
            if subzone not in exploredSubzones:
                zoneObj = Glob.zones.getZone(subzone)
                session.add(zoneObj)
                zoneObj.setStatus(status)
                exploredSubzones.update(subzone)
        session.commit()
        session.close()

    def arm(self, status='armed'):
        self.changeStatus(status)

    def disarm(self, status='ready'):
        self.changeStatus(status)

    def changeStatus(self, status='ready'):
        if self.status == status:
            return
        oldStatus = self.status
        session = Glob.dbSession()
        self.setStatus(status)
        session.add(self)
        session.commit()
        session.close()
        Glob.logger.info("zone %s  %s -> %s" %
                         (self.zone_name, oldStatus, status))

    def ready(self):
        return self.status == 'ready'

    def armed(self):
        return self.status == 'armed'

    def autoarmed(self):
        return self.status == 'autoarmed'

    def noSensor(self, interval=30):
        '''
            return boolean - true if there is no sensor event in previous "interval" in minutes
        '''
        for deviceName in self.getDevices():
            device = Glob.devices.getDevice(deviceName)
            if device is not None and device.hasSensorEvent(interval):
                return False
        return True
        