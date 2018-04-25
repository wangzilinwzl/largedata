import sys
import time
sys.path.append('/Users/shilei/MTA/website_test/utils')
from aws import getResource
from Incorporation import Incorporation
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, date
DYNAMODB_TABLE_NAME = 'mta_'+datetime.today().strftime("%A")

def routePlan(startStop,destinationStop):
	dynamodb = getResource('dynamodb', 'us-east-1')
	table_dynamo = dynamodb.Table(DYNAMODB_TABLE_NAME)

	# for local line 6 with express 4 & 5
	# similar to local line 1 with express 2 & 3, but more complex in some degree
	# as the limited time, for 4, 5, 6 lines, only give best route to Grand Central - 125st from north and 125st from south
	if 601 <= startStop <= 621 and startStop < destinationStop:
		# The direction is S, that is from uptown to downtown
		# The startStop has only local (6) train,
		# set the destination 631 (Grand Central - 125st) as default
		destinationStop = 631

		# all local trains which can reach my destination:
		localTrains = []
		search = table_dynamo.scan(FilterExpression=Attr('routeId').eq('6') & Attr('direction').eq('S'))
		trainsDict = search['Items']
		for trainDict in trainsDict:
			train = Incorporation()
			train.constructFromDyDict(trainDict)
			if unicode(str(startStop) + 'S') in train.futureStops and u'631S' in train.futureStops:
				localTrains.append(train)
		if len(localTrains) == 0:
			print 'no local train meets your requirements now, please wait.'
			return 'no local train meets your requirements now, please wait.'
		else:
			print 'there are {0} local train to Grand Central - 42st'.format(len(localTrains))

		# if only take the earlist local train, the duration
		arrivalTime_local = None # time for local trains arriving at start stop
		arrivalTrain_local = None #  all local trains available from start stop to destination stops		
		arrivalTimes_local = [(train.futureStops[u'631S'][0], train) for train in localTrains]
		if len(arrivalTimes_local) > 0:
			arrivalTime_local,arrivalTrain_local = min(arrivalTimes_local) # pick the earlist arriving local train
		startTime_local = arrivalTrain_local.futureStops[unicode(str(startStop) + 'S')][0]
		duration_local = (arrivalTime_local - startTime_local)/60.0
		print "The time spent with earlist local train to Grand Central - 42st is",duration_local,"min"

		# all possible express to switch
		startTime_express = arrivalTrain_local.futureStops[unicode(str(startStop) + 'S')][0]
		nearestTrain_125_local = None # earlist local train to 125st
		nearestTime_125_local = None
		arrivalTimes_125_local = [(train.futureStops[u'621S'][0], train) for train in localTrains]
		if len(arrivalTimes_125_local) > 0:
			nearestTime_125_local,nearestTrain_125_local = min(arrivalTimes_125_local) # pick the earlist train to 125st
		else:
			print 'no local train pass 125st at present, you can only stay on the local train'
			return 'no local train pass 125st at present, you can only stay on the local train'
		startTime_125 = nearestTrain_125_local.futureStops[u'621S'][0] # time the earlist train at 125st

		expressTrains = []
		search = table_dynamo.scan(FilterExpression=(Attr('routeId').eq('4') | Attr('routeId').eq('5')) & Attr('direction').eq('S'))
		trainsDict = search['Items']
		for trainDict in trainsDict:
			train = Incorporation()
			train.constructFromDyDict(trainDict)
			if u'621S' in train.futureStops and u'631S' in train.futureStops:
				expressTrains.append(train)
		if len(expressTrains) == 0:
			print 'no express train stop at 125st, you can stay on local train and update the app later'
			return 'no express train stop at 125st, you can stay on local train and update the app later'
		else:
			print 'there are {0} express train to 125st where you can switch'.format(len(expressTrains))

		# nearest express to switch
		nearestTrain_125_express = None
		nearestTime_125_express = None
		# get all express which pass 96st and arrival time later than the earlist local train
		arrivalTimes_125_express = [ (train.futureStops[u'621S'][0], train) for train in expressTrains if train.futureStops[u'621S'][0] > startTime_125 ]
		if len(arrivalTimes_125_express) > 0:
			nearestTime_125_express, nearestTrain_125_express = min(arrivalTimes_125_express)
		else:
			print 'no express train possible to switch at 125st now, you can stay on local train and update the app later'
			return 'no express train possible to switch at 125st now, you can stay on local train and update the app later'
		arrivalTime_express = nearestTrain_125_express.futureStops[u'631S'][0] # time the express train arriving at 42st
		duration_express = (arrivalTime_express - startTime_express)/60.0
		print "The time spent with switching to express to Grand Central - 42st is",duration_express,"min"

		if duration_express < duration_local:
			print 'You need to change to the express at 125st to Grand Central - 42st'
			return 'You need to change to the express at 125st to Grand Central - 42st'
		else:
			print "Stay on your local train is faster"
			return "Stay on your local train is faster"

	# The direction is N, that is from downtown to uptown
	elif 631 <= startStop <= 640 and startStop > destinationStop:
		destinationStop = 621

		# all local trains which can reach my destination:
		localTrains = []
		search = table_dynamo.scan(FilterExpression=Attr('routeId').eq('6') & Attr('direction').eq('N'))
		trainsDict = search['Items']
		for trainDict in trainsDict:
			train = Incorporation()
			train.constructFromDyDict(trainDict)
			if unicode(str(startStop) + 'N') in train.futureStops and u'621N' in train.futureStops:
				localTrains.append(train)
		if len(localTrains) == 0:
			print 'no local train meets your requirements now, please wait.'
			return 'no local train meets your requirements now, please wait.'
		else:
			print 'there are {0} local train to 125st'.format(len(localTrains))

		# if only take the earlist local train, the duration
		arrivalTime_local = None # time for local trains arriving at start stop
		arrivalTrain_local = None #  all local trains available from start stop to destination stops		
		arrivalTimes_local = [(train.futureStops[u'621N'][0], train) for train in localTrains]
		if len(arrivalTimes_local) > 0:
			arrivalTime_local,arrivalTrain_local = min(arrivalTimes_local) # pick the earlist arriving local train
		startTime_local = arrivalTrain_local.futureStops[unicode(str(startStop) + 'N')][0]
		duration_local = (arrivalTime_local - startTime_local)/60.0
		print "The time spent with earlist local train to 125st is",duration_local,"min"

		# all possible express to switch
		startTime_express = arrivalTrain_local.futureStops[unicode(str(startStop) + 'N')][0]
		nearestTrain_42_local = None # earlist local train to 125st
		nearestTime_42_local = None
		arrivalTimes_42_local = [(train.futureStops[u'631N'][0], train) for train in localTrains]
		if len(arrivalTimes_42_local) > 0:
			nearestTime_42_local,nearestTrain_42_local = min(arrivalTimes_42_local) # pick the earlist train to 125st
		else:
			print 'no local train pass 125st at present, you can only stay on the local train'
			return 'no local train pass 125st at present, you can only stay on the local train'
		startTime_42 = nearestTrain_42_local.futureStops[u'631N'][0] # time the earlist train at 125st

		expressTrains = []
		search = table_dynamo.scan(FilterExpression=(Attr('routeId').eq('4') | Attr('routeId').eq('5')) & Attr('direction').eq('S'))
		trainsDict = search['Items']
		for trainDict in trainsDict:
			train = Incorporation()
			train.constructFromDyDict(trainDict)
			if u'621N' in train.futureStops and u'631N' in train.futureStops:
				expressTrains.append(train)
		if len(expressTrains) == 0:
			print 'no express train stop at Grand Central - 42st, you can stay on local train and update the app later'
			return 'no express train stop at Grand Central - 42st, you can stay on local train and update the app later'
		else:
			print 'there are {0} express train to Grand Central - 42st where you can switch'.format(len(expressTrains))

		# nearest express to switch
		nearestTrain_42_express = None
		nearestTime_42_express = None
		# get all express which pass 96st and arrival time later than the earlist local train
		arrivalTimes_42_express = [ (train.futureStops[u'631N'][0], train) for train in expressTrains if train.futureStops[u'631N'][0] > startTime_42 ]
		if len(arrivalTimes_42_express) > 0:
			nearestTime_42_express, nearestTrain_42_express = min(arrivalTimes_42_express)
		else:
			print 'no express train possible to switch at 125st now, you can stay on local train and update the app later'
			return 'no express train possible to switch at 125st now, you can stay on local train and update the app later'
		arrivalTime_express = nearestTrain_42_express.futureStops[u'621N'][0] # time the express train arriving at 42st
		duration_express = (arrivalTime_express - startTime_express)/60.0
		print "The time spent with switching to express to 125st is",duration_express,"min"

		if duration_express < duration_local:
			print 'You need to change to the express at Grand Central - 42st to 125st'
			return 'You need to change to the express at Grand Central - 42st to 125st'
		else:
			print "Stay on your local train is faster"
			return "Stay on your local train is faster"



if __name__ == "__main__":
	print "input start stop"
	start = input()
	print "input destination stop"
	destination = input()
	routePlan(start,destination)












