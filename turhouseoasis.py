# -*- coding: utf-8 -*-

import schedule
import time
import importlib
import logging
import re

from glob import Glob
from drivers.oasisunit import OasisUnit
from dborm import turhousedb


class TurhouseOasisDriverError(Exception):
    pass


class TurhouseOasis(object):

    '''
        Daemon servicing oasis units
    '''

    def __init__(self):
        '''
            init oasis daemon
        '''
        # dict of units (dongles)
        self.units = {}
        # dict of driver object indexed by device id
        self.devices = {}
        self.lastSchedule = time.time()

        Glob.loggerOasis = logging.getLogger('oasis')

    def main(self):
        '''
            main loop reading messages from oasis devices
        '''
        self.initUnits()
        while True:
            self.listen()
            self.checkDriversTimeout()
            if time.time() - self.lastSchedule > 1:
                self.lastSchedule = time.time()
                schedule.run_pending()
            time.sleep(0.05)

    def initUnits(self):
        '''
            create listening device for each oasis dongle
        '''
        for unit in Glob.config.oasisUnits():
            unitObj = OasisUnit(unit)
            self.units[unit] = unitObj
            Glob.devices.registerDevice(unit, unitObj)
            unitParams = Glob.config.getUnitParams(unit)
            if 'pgx' in unitParams and unitParams['pgx']:
                (u, deviceId, deviceType) = Glob.config.getDeviceId(
                    unitParams['pgx'])
                unitObj.pgx = self.createDeviceInstance(
                    unit, deviceId, deviceType, unitParams['pgx'])
            if 'pgy' in unitParams and unitParams['pgy']:
                (u, deviceId, deviceType) = Glob.config.getDeviceId(
                    unitParams['pgy'])
                unitObj.pgy = self.createDeviceInstance(
                    unit, deviceId, deviceType, unitParams['pgy'])

    def listen(self):
        '''
            read & process available messages from oasis dongles
        '''
        for unit in Glob.config.oasisUnits():
            if self.units[unit].reader:
                msg = self.units[unit].reader.next()
                m = re.search("^\[(\d{8})\]\s", msg)
                if m:
                    msgDict = self.parseOasisMessage(unit, msg)
                    self.logOasisMessage(msgDict['name'], msg)
                    self.processMessage(unit, msgDict)
                elif msg == 'OK':
                    Glob.loggerOasis.info(msg)
                else:
                    Glob.loggerOasis.warning('Unknown mesage: ' + msg)

    def checkDriversTimeout(self):
        '''
            check if there is some 'timeouted' driver (eg. timeouted sequence of controller)
        '''
        for unit in self.units:
            self.units[unit].checkTimeout()
        for devId in self.devices:
            self.devices[devId].checkTimeout()

    def parseOasisMessage(self, unitName, msg):
        '''
            create struct with name from oasis message string
        '''
        p = msg.split()
        r = {}
        r['id'] = int(p[0][1:-1])
        r['type'] = p[1]
        r['name'] = Glob.config.getDeviceName(unitName, r['id'])
        if not r['name']:
            Glob.logger.warning('Unknown oasis device %d' % r['id'])
            r['name'] = self.createUnknownDevice(unitName, r['type'], r['id'])
        r['msg'] = p
        return r

    def logOasisMessage(self, name, msg):
        '''
            log oasis event record into the logfile
        '''
        Glob.loggerOasis.info(name + ", " + msg)

    def processMessage(self, unit, msgDict):
        '''
            process parsed message, do lookup in initialized devices, create new device instance if device not found
            and call processMessageSession method of device instance
        '''
        deviceId = msgDict['id']
        if not deviceId in self.devices:
            # create device instance
            self.createDeviceInstance(
                unit, deviceId, msgDict['type'], msgDict['name'])
        # process message
        self.devices[deviceId].processMessageSession(msgDict)

    def oasisDeviceDriverClass(self, deviceType):
        '''
          return name of class implemening driver for given deviceType
        '''
        drivers = {
            # socket    - SND/RCV
            'AC-88': 'OasisRelay',
            # horn      - SND/RCV
            'AC-80L': 'OasisInternalHorn',
                      # magnet uni - SND
                      'JA-81M': 'OasisGenericSensor',
                      # vibration detector - SND
                      'JA-82SH': 'OasisGenericSensor',
                      # magnet mini - SND
                      'JA-83M': 'OasisGenericSensor',
                      # PIR - SND
                      'JA-83P': 'OasisGenericSensor',
                      # controller - SND
                      'RC-86K': 'OasisController86K',
                      # thermostat - SND
                      'TP-82N': 'OasisThermostat',
                      # smoke/temp - SND
                      'JA-85ST': 'OasisSmokeSensor',
                      # siren -
                      'JA-80L': 'OasisSiren',
        }

        if deviceType in drivers:
            return drivers[deviceType]
        else:
            raise TurhouseOasisDriverError(
                'Cannot find driver for device %s' % deviceType)

    def createDeviceInstance(self, unit, deviceId, deviceType, deviceName):
        '''
            initialize device driver and store it in self.devices dictionary
        '''
        deviceClass = self.oasisDeviceDriverClass(deviceType)
        module = importlib.import_module('drivers.' + deviceClass.lower())
        class_ = getattr(module, deviceClass)
        # get_or_create driver object
        session = Glob.dbSession()
        driverObj = turhousedb.get_or_create(
            session, class_, device_name=deviceName)
        driverObj.init()
        driverObj.setUnit(self.units[unit])
        driverObj.setOptions(Glob.config.getDeviceOptions(unit, deviceName))
        session.commit()
        session.close()
        # create lookup records
        self.devices[deviceId] = driverObj
        Glob.devices.registerDevice(deviceName, driverObj)
        if deviceType == 'RC-86K':
            id2 = deviceId ^ 1 << 20
            self.devices[id2] = driverObj
        return driverObj

    def createUnknownDevice(self, unit, deviceType, deviceId):
        '''
            create name & config item for not configured device ( unkonown_<type>_<serial_number> )
        '''
        devName = 'unknown_' + deviceType + '_' + str(deviceId)
        Glob.config.createDeviceConf(unit, devName, deviceType, deviceId)
        return devName
