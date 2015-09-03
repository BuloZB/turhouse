
class PoolError(Exception):
    pass


class Glob(object):

    '''
      object which contain all global objects
    '''


class Pool(object):

    def __init__(self):
        self.pool = {}

    def registerItem(self, name, item):
        '''
            insert item object into pool
        '''
        if name in self.pool:
            raise PoolError('Item name allready assigned %s' % name)
        else:
            self.pool[name] = item

    def getItem(self, name):
        '''
            return object from pool by name
        '''
        try:
            return self.pool[name]
        except KeyError:
            return None

    def getItems(self):
        return self.pool


class DevicePool(Pool):

    def __init__(self):
        Pool.__init__(self)

    def registerDevice(self, name, device):
        '''
            insert device object into pool
        '''
        self.registerItem(name, device)

    def getDevice(self, name):
        '''
            return device driver instance of device
        '''
        return self.getItem(name)

    def getDevices(self):
        return self.getItems()


class ZonePool(Pool):

    def __init__(self):
        Pool.__init__(self)

    def registerZone(self, name, zone):
        '''
            insert zone object into pool
        '''
        self.registerItem(name, zone)

    def getZone(self, name):
        '''
            return zone instance by name
        '''
        return self.getItem(name)

    def getZones(self):
        return self.getItems()
