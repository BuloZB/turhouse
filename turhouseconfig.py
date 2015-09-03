# -*- coding: utf-8 -*-

from configobj import ConfigObj

import time

'''
    Turhouse config reader/writer
'''


class TurhouseConfigError(Exception):
    pass


class TurhouseConfig(object):

    def __init__(self, configfile=''):
        '''
            read configuration file
        '''
        self.configfile = configfile
        if configfile == '':
            self.configfile = 'turhouse.conf'
        self.config = ConfigObj(self.configfile)
        self.deviceNameLookup = {}
        self.idLookup = {}

        self.enhanceOasisDevicesConfig()

    def enhanceOasisDevicesConfig(self):
        '''
            enhance oasis devices internal config structure
            create by ID lookup dictionary & insert RC-86K second part
        '''
        for unit in self.oasisUnits():
            self.idLookup[unit] = {}
            devices = self.config[unit]['devices'].keys()
            for deviceName in devices:
                deviceConf = self.config[unit]['devices'][deviceName]
                deviceId = int(deviceConf['id'])
                self.initIdLookup(
                    unit, deviceId, deviceName, deviceConf['type'])

    def initIdLookup(self, unit, deviceId, deviceName, deviceType):
        '''
            create record in idLookup & deviceNameLookup dictionary
        '''
        self.deviceNameLookup[deviceName] = (unit, deviceId, deviceType)
        self.idLookup[unit][deviceId] = deviceName
        if deviceType == 'RC-86K':
            id2 = deviceId | 1 << 20
            self.idLookup[unit][id2] = deviceName

    def daemons(self):
        '''
             returns config of daemons
        '''
        try:
            return self.config['main']['daemons']
        except KeyError:
            raise TurhouseConfigError(
                "No daemon configured in config file '%s'" % self.configfile)

    def oasisUnits(self):
        '''
             returns config of available oasis units
        '''
        try:
            return self.config['TurhouseOasis']['units']
        except KeyError:
            return []

    def getAlarmZones(self):
        '''
             returns config of available oasis units
        '''
        try:
            return self.config['alarm_zones']
        except KeyError:
            return []

    def smtp(self):
        '''
             returns smtp configuration
        '''
        try:
            return self.config['smtp']
        except KeyError:
            return None

    def db(self):
        '''
             returns db configuration
        '''
        return self.config['main']['db']

    def notification(self):
        '''
             returns list of email addresses to notify
        '''
        try:
            return self.config['notification']
        except KeyError:
            return None

    def loggingConf(self):
        '''
             returns path to logging config
        '''
        try:
            return self.config['main']['logging_conf']
        except KeyError:
            return 'turhouse_logging.conf'

    def getDeviceName(self, unit, deviceId):
        '''
             returns name of item based on unit & id
        '''
        try:
            return self.idLookup[unit][deviceId]
        except KeyError:
            return None

    def getDeviceId(self, deviceName):
        '''
             returns device item based on name
        '''
        try:
            return self.deviceNameLookup[deviceName]
        except KeyError:
            return None

    def getDeviceOptions(self, unit, deviceName):
        '''
            retrn options dict or None
        '''
        try:
            return self.config[unit]['devices'][deviceName]['options']
        except KeyError:
            return None

    def getUnitParams(self, unit):
        '''
              returns params of unit
        '''
        try:
            return self.config[unit]['params']
        except KeyError:
            return None

    def createDump(self, filename='', addTimestamp=False):
        '''
            dump current config into the file
        '''
        if filename == '':
            filename = 'turhouse.conf.dump'
        if addTimestamp:
            filename += time.strftime("_%y%m%d_%H:%M:%S")
        self.config.filename = filename
        self.config.write()

    def createDeviceConf(self, unit, deviceName, deviceType, deviceId):
        '''
            create configuration for new device
        '''
        self.initIdLookup(unit, deviceId, deviceName, deviceType)
        self.config[unit]['devices'][deviceName] = {
            'type': deviceType, 'id': deviceId}
        self.createDump()
