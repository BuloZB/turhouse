#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glob import *
import turhouseconfig
from event import notification

configfile = ''
Glob.config = turhouseconfig.TurhouseConfig(configfile)
notification.ezs_notification('Test: ', 'Test Device', 'Test event')
