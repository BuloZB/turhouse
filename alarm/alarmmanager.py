# -*- coding: utf-8 -*-


from glob import Glob
from alarmzone import AlarmZone
from dborm import turhousedb
from event.basemanager import BaseManager


class AlarmManager(BaseManager):

    '''
      turhouse manager object
    '''

    def __init__(self):
        BaseManager.__init__(self)
        # init alarm zones
        session = Glob.dbSession()
        zones = Glob.config.getAlarmZones()
        for zoneName in zones:
            zone = turhousedb.get_or_create(
                session, AlarmZone, zone_name=zoneName)
            zone.init()
            session.add(zone)
            Glob.zones.registerZone(zoneName, zone)
            if 'status' in zones[zoneName]:
                zone.setStatus(zones[zoneName]['status'])
            if 'devices' in zones[zoneName]:
                for device in zones[zoneName]['devices']:
                    zone.addDevice(device)
            if 'subzones' in zones[zoneName]:
                for subzoneName in zones[zoneName]['subzones']:
                    if subzoneName in zones:
                        zone.addSubzone(subzoneName)
                    else:
                        Glob.logger.error(
                            "Unknown subzone %s -> %s " % (zoneName, subzoneName))
        session.commit()
        session.close()
        # atach event handlers
        self.sensorEvent += self.sensorEventHandler
        self.tamperEvent += self.tamperEventHandler
        self.controllerEvent += self.controllerEventHandler
        self.buttonEvent += self.buttonEventHandler

        for zoneName in zones:
            zone = Glob.zones.getZone(zoneName)
            Glob.logger.info(
                "Zone %s devices: %s " % (zoneName, zone.getDevices()))

    def tamperEventHandler(self, sender, event_type, params):
        Glob.logger.info(
            "Tamper %s " % sender)
        self.alarm(sender, event_type)

    def controllerEventHandler(self, sender, event_type, params):
        Glob.logger.info(
            "Controller %s code: %s " % (sender, params['code']))

    def sensorEventHandler(self, sender, event_type, params):
        if self.isDeviceArmed(sender):
            Glob.logger.info(
                "Sensor %s status: %s " % (sender, params['status']))
            self.alarm(sender, event_type, params)
        elif self.isDeviceArmed(sender, 'autoarmed'):
            Glob.logger.info(
                "Sensor %s status: %s " % (sender, params['status']))
            self.autoAlarm(sender, event_type, params)

    def buttonEventHandler(self, sender, event_type, params):
        Glob.logger.info(
            "Button %s " % sender)

    def isDeviceArmed(self, deviceName, status='armed'):
        for zoneName in Glob.zones.getZones():
            cZone = self.zone(zoneName)
            if cZone.isArmed(status):
                if cZone.hasDevice(deviceName):
                    Glob.logger.info(
                        "Zone %s ststus: %s, device: %s " % (zoneName, status, deviceName))
                    return True
        return False

    def alarm(self):
        '''
            method called in case of sensor event in armed zone
            action has to be set in child class
        '''
        pass

    def autoAlarm(self):
        '''
            method called in case of sensor event in autoarmed zone
        '''
        self.alarm()
