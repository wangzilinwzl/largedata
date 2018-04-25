from collections import OrderedDict
# Storing trip related data
# Note : some trips wont have vehicle data
class tripupdate(object):
	def __init__(self):
	    self.tripId = None # unique trip identifier, trip_id
	    self.routeId = None # train number, route_id
	    self.startDate = None # start_date
	    self.direction = None # got from tripId
	    self.vehicleData = None # info from vehicle related to tripupdate
	    # futureStops, stop_time_update: arrival (time); departure (time); route_id
	    self.futureStops = OrderedDict() # Format {stopId : [arrivalTime,departureTime]}





