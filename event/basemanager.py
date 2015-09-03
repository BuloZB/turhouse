# -*- coding: utf-8 -*-


from glob import Glob
from event.eventhook import EventHook


class BaseManager(object):

    '''
      turhouse base manager object implementing event processing with hooks
    '''

    def __init__(self):
        # define Events
        self.sensorEvent = EventHook()
        self.tamperEvent = EventHook()
        self.controllerEvent = EventHook()
        self.buttonEvent = EventHook()
        self.beaconEvent = EventHook()

    def processEvent(self, sender, event_type, params):
        try:
            hook = getattr(self, event_type.lower() + 'Event')
        except AttributeError:
            Glob.logger.error(
                "Unknown event %s sender: %s" % (event_type, sender))
        if hook is not None:
            hook.fire(sender, event_type, params)

    def device(self, deviceName):
        return Glob.devices.getDevice(deviceName)

    def zone(self, zoneName):
        return Glob.zones.getZone(zoneName)
