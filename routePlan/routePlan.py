import sys
import time
sys.path.append('../utils')
from aws import getResource
from Incorporation import Incorporation
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, date
DYNAMODB_TABLE_NAME = 'mta_'+datetime.today().strftime("%A")

def routePlan2(startStop,destinationStop):
	dynamodb = getResource('dynamodb', 'us-east-1')
	table_dynamo = dynamodb.Table(DYNAMODB_TABLE_NAME)

	# for local line 1 with express 2 & 3
	if 101 <= startStop <= 140 and 101 <= destinationStop <= 140:
		if startStop < destinationStop and startStop <= 120 and destinationStop >= 127: # direction: S
			#startTime_local =  int(time.time())
			#startTime_express = int(time.time())

			# step 1: assume I just arrive at the station, all arrival local trains which can reach my destination
			localTrains = []
			search = table_dynamo.scan(FilterExpression=Attr('routeId').eq('1') & Attr('direction').eq('S'))
			trainsDict = search['Items']
			for trainDict in trainsDict:
				train = Incorporation()
				train.constructFromDyDict(trainDict)
				# startStop => 96th => 42th => destinationStop
				if unicode(str(startStop) + 'S') in train.futureStops and u'120S' in train.futureStops and unicode(str(destinationStop) + 'S') in train.futureStops: # if my stop and 96 exist
					localTrains.append(train)
			if len(localTrains) == 0:
				print 'no local train stop meeting your requirements, please wait.'
				return 'no local train stop meeting your requirements, please wait.'
			else:
				print 'there are {0} local train to your destination and pass 96st'.format(len(localTrains))
			
			# step 2: if only take the local train, the shortest arrival time
			arrivalTime_local = None
			arrivalTrain_local = None			
			arrivalTimes_local = [(train.futureStops[unicode(str(destinationStop) + 'S')][0], train) for train in localTrains]
			if len(arrivalTimes_local) > 0:
				arrivalTime_local,arrivalTrain_local = min(arrivalTimes_local)
			startTime_local = arrivalTrain_local.futureStops[unicode(str(startStop) + 'S')][0]
			duration_local = (arrivalTime_local - startTime_local)/60.0
			print "The time spent with earlist local train is",duration_local,"min"


			# step 3: if switch, the shortest time
			# step 3_1: the shortest time for local from startStop to 96st
			startTime_express = arrivalTrain_local.futureStops[unicode(str(startStop) + 'S')][0]

			nearestTrain_96_local = None
			nearestTime_96_local = None
			arrivalTimes_96_local = [(train.futureStops[u'120S'][0], train) for train in localTrains]
			if len(arrivalTimes_96_local) > 0:
				nearestTime_96_local,nearestTrain_96_local = min(arrivalTimes_96_local)
			startTime_96 = nearestTrain_96_local.futureStops[u'120S'][0] # time the local train I take arriving at 96st

			expressTrains = []
			search = table_dynamo.scan(FilterExpression=(Attr('routeId').eq('2') | Attr('routeId').eq('3')) & Attr('direction').eq('S'))
			trainsDict = search['Items']
			for trainDict in trainsDict:
				train = Incorporation()
				train.constructFromDyDict(trainDict)
				if u'120S' in train.futureStops and u'127S' in train.futureStops:
					expressTrains.append(train)
			if len(expressTrains) == 0:
				print 'no express train stop at 96st, you can take local train and update the app later'
				return 'no express train stop at 96st, you can take local train and update the app later'
			else:
				print 'there are {0} express train to 96st where you can switch'.format(len(expressTrains))

			nearestTrain_96_express = None
			nearestTime_96_express = None
			arrivalTimes_96_express = [ (train.futureStops[u'120S'][0], train) for train in expressTrains if train.futureStops[u'120S'][0] > startTime_96 ]
			if len(arrivalTimes_96_express) > 0:
				nearestTime_96_express, nearestTrain_96_express = min(arrivalTimes_96_express)
			duration_express_1 = nearestTime_96_express - startTime_express
			startTime_42 = nearestTrain_96_express.futureStops[u'127S'][0] # time the express train I may switch arriving at 42st

			# step 3_2: time for express from 96st to 42st
			duration_express_2 = nearestTrain_96_express.futureStops[u'127S'][0] - nearestTime_96_express

			# step 3_3: time for whether to change to local again
			if unicode(str(destinationStop) + 'S') in nearestTrain_96_express.futureStops:
				duration_express_3 = nearestTrain_96_express.futureStops[unicode(str(destinationStop) + 'S')][0]
			else:
				nearestTrain_42_local = None
				nearestTime_42_local = None
				arrivalTimes_42_local = [(train.futureStops[u'127S'][0], train) for train in localTrains if train.futureStops[u'127S'][0] > startTime_42]
				if len(arrivalTimes_42_local) > 0:
					nearestTime_42_local, nearestTrain_42_local = min(arrivalTimes_42_local)
				duration_express_3 = nearestTrain_42_local.futureStops[unicode(str(destinationStop) + 'S')][0] - nearestTime_42_local

			# step 3_4: add all time together
			duration_express = (duration_express_1 + duration_express_2 + duration_express_3)/60.0
			print "The time spent with switching to express at 96st is",duration_express,"min"


















			# step 3: get the earlist local train arriving 96st
			nearestTrain_local = None
			nearestTime_local = None
			arrivalTimes_local = [(train.futureStops[u'120S'][0], train) for train in localTrains]	
			if len(arrivalTimes_local) > 0:
				nearestTime_local, nearestTrain_local = min(arrivalTimes_local)
			nearestTime_local = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(nearestTime_local))

			startTime = nearestTrain_local.futureStops[u'120S'][0]

			# step 4: get the earlist express train arriving at 96st after the earlist local train
			nearestTrain_express = None
			nearestTime_express = None
			arrivalTimes_express = [ (train.futureStops[u'120S'][0], train) for train in expressTrains if train.futureStops[u'120S'][0] > startTime ]
			if len(arrivalTimes_express) > 0:
				nearestTime_express, nearestTrain_express = min(arrivalTimes_express)
			nearestTime_express = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(nearestTime_express))

			# step 5: decide whether to switch
			arrival_at_stop42_local = nearestTrain_local.futureStops[u'127S'][0]
			arrival_at_stop42_express = nearestTrain_express.futureStops[u'127S'][0]
			startTime_original =  nearestTrain_local.futureStops[unicode(str(startStop) + 'S')][0]
			duration_local = arrival_at_stop42_local - startTime_original
			duration_local = duration_local/60.0
			duration_express= arrival_at_stop42_express - startTime_original
			duration_express = duration_express/60.0
			print ('The next local train will arrive at 42nd st in {0}').format(duration_local) + " minutes"
			print ('The next express train will arrive at 42nd st in {0}').format(duration_express) + " minutes"
			
			if duration_local > duration_express:
				print 'Switch to Express Train'
				return 'Switch to Express Train'
			else:
				print 'Stay on in the Local Train'
				return 'Stay on in the Local Train'


		elif startStop > destinationStop and startStop >=127 and destinationStop <= 120: # direction: N
			localTrains1 =[]
			search1= table_dynamo.scan(FilterExpression=Attr('routeId').eq('1') & Attr('direction').eq('N'))
			trainsDict1 = search1['Items']
			for trainDict in trainsDict1:
				train1 = Incorporation()
				train1.constructFromDyDict(trainDict)
				if unicode(str(startStop) + 'N') in train1.futureStops and u'127N' in train1.futureStops: # if my stop and 42st exists
					localTrains1.append(train1)
			print 'there are {0} local train to 42st'.format(len(localTrains1))
			if len(localTrains1) == 0:
				print 'no local train stop at your startStop'
				return 'no local train stop at your startStop'

			expressTrains1 = []
			search1 = table_dynamo.scan(FilterExpression=(Attr('routeId').eq('2') | Attr('routeId').eq('3')) & Attr('direction').eq('N'))
			trainsDict1 = search['Items']
			for trainDict in trainsDict1:
				train1 = Incorporation()
				train1.constructFromDyDict(trainDict)
				if u'127N' in train1.futureStops:
					expressTrains1.append(train1)
			print 'there are {0} express train to 42st'.format(len(expressTrains1))
			if len(expressTrains1) == 0:
				print 'no express train stop at: 42st, you can only take local train'
				return 'no express train stop at: 42st, you can only take local train'

			nearestTrain_local1 = None
			nearestTime_local1 = None
			arrivalTimes_local1 = [(train.futureStops[u'127N'][0], train) for train in localTrains1]	
			if len(arrivalTimes_local1) > 0:
				nearestTime_local1, nearestTrain_local1 = min(arrivalTimes_local1)
			nearestTime_local1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(nearestTime_local1))

			startTime = nearestTrain_local1.futureStops[u'127N'][0]

			nearestTrain_express1 = None
			nearestTime_express1 = None
			arrivalTimes_express1 = [ (train.futureStops[u'120N'][0], train) for train in expressTrains1 if train.futureStops[u'127N'][0] > startTime ]
			if len(arrivalTimes_express1) > 0:
				nearestTime_express1, nearestTrain_express1 = min(arrivalTimes_express)
			nearestTime_express1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(nearestTime_express1))

			arrival_at_stop42_local1 = nearestTrain_local1.futureStops[u'120N'][0]
			arrival_at_stop42_express1 = nearestTrain_express1.futureStops[u'120N'][0]
			startTime_original1 =  nearestTrain_local1.futureStops[unicode(str(startStop) + 'N')][0]
			duration_local1 = arrival_at_stop42_local1 - startTime_original1
			duration_local1 = duration_local1/60.0
			duration_express1 = arrival_at_stop42_express1 - startTime_original1
			duration_express1 = duration_express1/60.0
			print ('The next local train will arrive at 96th st in {0}').format(duration_local1) + " minutes"
			print ('The next express train will arrive at 96th st in {0}').format(duration_express1) + " minutes"
			
			if duration_local1 > duration_express1:
				print 'Switch to Express Train'
				return 'Switch to Express Train'
			else:
				print 'Stay on in the Local Train'
				return 'Stay on in the Local Train'

		else:
			print "No need to change to express trains, just take the first local train"


	# for lcoal line 4 & 6 with express line 5
	if 401 <= startStop <= 640 and 401 <= destinationStop <= 640:
		
		if 601 <= startStop <= 640 and 601 <= startStop <=640


















