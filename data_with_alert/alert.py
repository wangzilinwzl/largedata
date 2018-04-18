# Storing alerts from the feed
class alert(object):
    alertMessage = None
    tripId = [] # unique trip identifier
    routeId  = {} # train number
    def __init__(self):
        self.tripId = []
        self.routeId = {}