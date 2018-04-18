# -*- coding: UTF-8 -*-
from collections import OrderedDict
import re
import ast

class Incorporation:
	def __init__(self):
		self.tripId = None # unique trip identifier, both trip_update and vehicle have
		self.routeId = None # mainly for trip_update
		self.startDate = None # trip_update
		self.direction = None # from trip_id
		self.currentStopId = None # from vehicle
		self.currentStopStatus = None # from vehicle
		self.vehicleTimeStamp = None # timestamp from vehicle info
		self.futureStops = OrderedDict() # stop_time_updated， # Format {stopId : [arrivalTime,departureTime]}
		self.timeStamp = None
		self.alert = None

	def constructFromDyDict(self,d): # construct dynamically 
		self.tripId = d[u'tripId']
		self.routeId = d[u'routeId']
		self.startDate = d[u'startDate']
		self.direction = d[u'direction']
		self.currentStopId = d[u'currentStopId']
		self.currentStopStatus = d[u'currentStopStatus']
		self.vehicleTimeStamp = d[u'vehicleTimeStamp']
		m = re.match(r'^OrderedDict\((.+)\)$', d[u'futureStops'])
		if m:
			self.futureStops = OrderedDict(ast.literal_eval(m.group(1)))
		self.timeStamp = d[u'timestamp']
		self.alert = d[u'alert']