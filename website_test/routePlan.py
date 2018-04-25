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

	# for local line 1 with express 2 & 3
	if 101 <= startStop <= 140 and 101 <= destinationStop <= 140:
		# The direction is S, that is from uptown to downtown
		# The startStop has only local (1) train, the destination go through 96st and 42st
		# We need to decide whether to switch to express at 96st and whether to switch back to local at 42st
		if startStop < destinationStop and startStop <= 120 and destinationStop >= 127:
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
				if unicode(str(startStop) + 'S') in train.futureStops and u'120S' in train.futureStops and unicode(str(destinationStop) + 'S') in train.futureStops: # if my stops and 96 exist
					localTrains.append(train)
			if len(localTrains) == 0:
				print 'no local train meets your requirements now, please wait.'
				return 'no local train meets your requirements now, please wait.'
			else:
				print 'there are {0} local train to your destination and pass 96st'.format(len(localTrains))
			
			# step 2: if only take the local train, the shortest arrival time
			arrivalTime_local = None # time for local trains arriving at start stop
			arrivalTrain_local = None #  all local trains available from start stop to destination stops		
			arrivalTimes_local = [(train.futureStops[unicode(str(destinationStop) + 'S')][0], train) for train in localTrains]
			if len(arrivalTimes_local) > 0:
				arrivalTime_local,arrivalTrain_local = min(arrivalTimes_local) # pick the earlist arriving local train
			startTime_local = arrivalTrain_local.futureStops[unicode(str(startStop) + 'S')][0]
			duration_local = (arrivalTime_local - startTime_local)/60.0
			print "The time spent with earlist local train is",duration_local,"min"


			# step 3: if switch, the shortest time
			# that is: take local first, then switch at 96st to express, then need to decide whether to switch back to local again at 42st
			# if destination is also on express, no need to change, if not, must change
			# calculate the total time
			# step 3_1: the shortest time for local from startStop to 96st
			startTime_express = arrivalTrain_local.futureStops[unicode(str(startStop) + 'S')][0] # as the start stop only has local train, so this is also the start time for route including express

			nearestTrain_96_local = None # earlist local train to 96st
			nearestTime_96_local = None
			arrivalTimes_96_local = [(train.futureStops[u'120S'][0], train) for train in localTrains]
			if len(arrivalTimes_96_local) > 0:
				nearestTime_96_local,nearestTrain_96_local = min(arrivalTimes_96_local) # pick the earlist train to 96st
			startTime_96 = nearestTrain_96_local.futureStops[u'120S'][0] # time the earlist train at 96st

			# get all possible express train which will arrive at 96st & 42st
			expressTrains = []
			search = table_dynamo.scan(FilterExpression=(Attr('routeId').eq('2') | Attr('routeId').eq('3')) & Attr('direction').eq('S'))
			trainsDict = search['Items']
			for trainDict in trainsDict:
				train = Incorporation()
				train.constructFromDyDict(trainDict)
				if u'120S' in train.futureStops and u'127S' in train.futureStops:
					expressTrains.append(train)
			if len(expressTrains) == 0:
				print 'no express train stop at 96st, you can stay on local train and update the app later'
				return 'no express train stop at 96st, you can stay on local train and update the app later'
			else:
				print 'there are {0} express train to 96st where you can switch'.format(len(expressTrains))

			nearestTrain_96_express = None 
			nearestTime_96_express = None
			# get all express which pass 96st and arrival time later than the earlist local train
			arrivalTimes_96_express = [ (train.futureStops[u'120S'][0], train) for train in expressTrains if train.futureStops[u'120S'][0] > startTime_96 ]
			if len(arrivalTimes_96_express) > 0:
				nearestTime_96_express, nearestTrain_96_express = min(arrivalTimes_96_express)
			else:
				print 'no express train possible to switch at 96st now, you can stay on local train and update the app later'
				return 'no express train possible to switch at 96st now, you can stay on local train and update the app later'
			duration_express_1 = nearestTime_96_express - startTime_express # time when switch to express - time when taking local from start stop
			startTime_42 = nearestTrain_96_express.futureStops[u'127S'][0] # time the express train arriving at 42st

			# step 3_2: time for express from 96st to 42st
			duration_express_2 = startTime_42 - nearestTime_96_express # time the express arrives at 42st - time when switch to express

			# step 3_3: time for whether to change to local again
			# if the express can reach the destination
			if unicode(str(destinationStop) + 'S') in nearestTrain_96_express.futureStops:
				# time the express arrives at the destination - time the express arrives at 42st
				duration_express_3 = nearestTrain_96_express.futureStops[unicode(str(destinationStop) + 'S')][0] - startTime_42
			# if the express cannot reach the destination
			# as the later train for local and express are the same, so just switch back to local at 42st
			else:
				nearestTrain_42_local = None
				nearestTime_42_local = None
				arrivalTimes_42_local = [(train.futureStops[u'127S'][0], train) for train in localTrains if train.futureStops[u'127S'][0] > startTime_42]
				if len(arrivalTimes_42_local) > 0:
					nearestTime_42_local, nearestTrain_42_local = min(arrivalTimes_42_local) # first local train arriving at 42st after the express arriving
				else:
					print 'no local train to switch back again, stay on express and update later'
					return 'no local train to switch back again, stay on express and update later'
				duration_express_3 = nearestTrain_42_local.futureStops[unicode(str(destinationStop) + 'S')][0] - startTime_42

			# step 3_4: add all time together
			duration_express = (duration_express_1 + duration_express_2 + duration_express_3)/60.0
			print "The time spent with switching to express at 96st is",duration_express,"min"


			# step 4: make final decision
			if duration_express < duration_local:
				if unicode(str(destinationStop) + 'S') in nearestTrain_96_express.futureStops:
					print "You need to change to the express at 96st to your destination"
					return "You need to change to the express at 96st to your destination"
				else:
					print "You need to change to the express at 96st and change back to local at 42st to your destination"
					return "You need to change to the express at 96st and change back to local at 42st to your destination"

			else:
				print "Stay on your local train is faster"
				return "Stay on your local train is faster"



		# The direction is N, that is from downtown to uptown
		elif startStop > destinationStop and startStop >=127 and destinationStop <= 120: 
			# if can take express at startStop			
			if startStop <= 137:
				# step 1: first choice, take express and change to local at 96st
				# step 1_1: get all available express trains
				expressTrains = []
				search = table_dynamo.scan(FilterExpression=(Attr('routeId').eq('2') | Attr('routeId').eq('3')) & Attr('direction').eq('N'))
				trainsDict = search['Items']
				for trainDict in trainsDict:
					train = Incorporation()
					train.constructFromDyDict(trainDict)
					if unicode(str(startStop) + 'N') in train.futureStops and u'120N' in train.futureStops:
						expressTrains.append(train)
				if len(expressTrains) == 0:
					print 'No express train at present, please try local trains'
					localTrains = []
					search= table_dynamo.scan(FilterExpression=Attr('routeId').eq('1') & Attr('direction').eq('N'))
					trainsDict = search['Items']
					for trainDict in trainsDict:
						train = Incorporation()
						train.constructFromDyDict(trainDict)
						if unicode(str(startStop) + 'N') in train.futureStops and unicode(str(destinationStop) + 'N') in train.futureStops:
							localTrains.append(train)
					if len(localTrains) == 0:
						print 'No local train at present too, you need to wait'
						return 'No local train at present too, you need to wait'
					else:
						print 'there are {0} local train to your destination'.format(len(localTrains))
					nearestTrain_local = None
					nearestTime_local = None
					arrivalTimes_local = [(train.futureStops[unicode(str(destinationStop) + 'N')][0], train) for train in localTrains]
					nearestTime_local, nearestTrain_local = min(arrivalTimes_local)
					duration = (nearestTrain_local.futureStops[unicode(str(destinationStop) + 'N')][0] - nearestTrain_local.futureStops[unicode(str(startStop) + 'N')][0])/60.0
					print 'take the earlist local train, it will cost you', duration,'min'
					return 'take the earlist local train, it will cost you', duration,'min'



				else:
					print 'there are {0} express train available'.format(len(expressTrains)) # if can take express from the start stop

				# step 1_2: get the all local train from 96st to destination
				localTrains =[]
				search= table_dynamo.scan(FilterExpression=Attr('routeId').eq('1') & Attr('direction').eq('N'))
				trainsDict = search['Items']
				for trainDict in trainsDict:
					train = Incorporation()
					train.constructFromDyDict(trainDict)
					if u'120N' in train.futureStops and unicode(str(destinationStop) + 'N') in train.futureStops:
						localTrains.append(train)
				if len(localTrains) == 0:
					print 'No local train to switch at 96st now, please update later'
					return 'No local train to switch at 96st now, please update later'
				else:
					print 'there are {0} local train to your destination'.format(len(localTrains))

				# step 1_3: get the earlist express train to 96st
				nearestTrain_express = None
				nearestTime_express = None
				arrivalTimes_express = [(train.futureStops[u'120N'][0], train) for train in expressTrains]
				if len(arrivalTimes_express) > 0:
					nearestTime_express, nearestTrain_express = min(arrivalTimes_express)
				startTime_express = nearestTrain_express.futureStops[unicode(str(startStop) + 'N')][0] # time to take express at start stop
				arrivalTime_express = nearestTrain_express.futureStops[u'120N'][0] # time the express arriving at 96st

				# step 1_4: get the earlist local train from 96st to destination
				nearestTrain_local = None
				nearestTime_local = None
				arrivalTimes_local = [(train.futureStops[u'120N'][0], train) for train in localTrains if train.futureStops[u'120N'][0] > arrivalTime_express]	
				if len(arrivalTimes_local) > 0:
					nearestTime_local, nearestTrain_local = min(arrivalTimes_local) # the earlist local train at 96st after the express
				arrivalTime_local = nearestTrain_local.futureStops[unicode(str(destinationStop) + 'N')][0] # its time to destination
				#startTime = min(nearestTrain_express.futureStops[unicode(str(startStop) + 'N')][0],nearestTrain_local.futureStops[unicode(str(startStop) + 'N')][0])
				startTime = nearestTrain_express.futureStops[unicode(str(startStop) + 'N')][0]
				duration_express = (arrivalTime_local - startTime)/60.0
				print 'Time taking express and switch to local at 96st is', duration_express,'min'


				
				# step 2: second choice, take local train only
				for trainDict in trainsDict:
					train = Incorporation()
					train.constructFromDyDict(trainDict)
					if unicode(str(destinationStop) + 'N') in train.futureStops and unicode(str(destinationStop) + 'N') in train.futureStops: 
						localTrains.append(train)
				if len(localTrains) == 0:
					print 'No local train your destination stop now, stay on express and update the app later'
					return 'No local train your destination stop now, stay on express and update the app later'
				else:
					print 'there are {0} local train to your destination'.format(len(localTrains))

				nearestTrain_local = None
				nearestTime_local = None
				arrivalTimes_local = [(train.futureStops[unicode(str(destinationStop) + 'N')][0], train) for train in localTrains]	
				if len(arrivalTimes_local) > 0:
					nearestTime_local, nearestTrain_local = min(arrivalTimes_local)
				arrivalTime_local = nearestTrain_local.futureStops[unicode(str(destinationStop) + 'N')][0]
				duration_local = (arrivalTime_local-startTime)/60.0
				print 'Time taking local train from startStop to destinationStop is', duration_local,'min'

				if duration_local < duration_express:
					print 'Take the earlist local train'
					return 'Take the earlist local train'
				else:
					print "Take the earlist express train and switch to local at 96st"
					return "Take the earlist express train and switch to local at 96st"

			# if the startStop is larger than 137, the start stop can only be local train
			else:
				# step 1: assume I just arrive at the station, all arrival local trains which can reach my destination
				localTrains = []
				search = table_dynamo.scan(FilterExpression=Attr('routeId').eq('1') & Attr('direction').eq('N'))
				trainsDict = search['Items']
				for trainDict in trainsDict:
					train = Incorporation()
					train.constructFromDyDict(trainDict)
					# startStop => 42th => 96th => destinationStop
					if unicode(str(startStop) + 'N') in train.futureStops and u'127N' in train.futureStops and unicode(str(destinationStop) + 'N') in train.futureStops: # if my stop and 96 exist
						localTrains.append(train)
				if len(localTrains) == 0:
					print 'no local train stop meeting your requirements, please wait.'
					return 'no local train stop meeting your requirements, please wait.'
				else:
					print 'there are {0} local train to your destination and pass 42st'.format(len(localTrains))

				# step 2: if only take the local train, the shortest arrival time
				arrivalTime_local = None
				arrivalTrain_local = None
				arrivalTimes_local = [(train.futureStops[unicode(str(destinationStop) + 'N')][0], train) for train in localTrains]
				if len(arrivalTimes_local) > 0:
					arrivalTime_local,arrivalTrain_local = min(arrivalTimes_local)
				startTime_local = arrivalTrain_local.futureStops[unicode(str(startStop) + 'N')][0]
				duration_local = (arrivalTime_local - startTime_local)/60.0
				print "The time spent with earlist local train is",duration_local,"min"	

				# step 3: if switch, the shortest time
				# step 3_1: the shortest time for local from startStop to 42st
				startTime_express = arrivalTrain_local.futureStops[unicode(str(startStop) + 'N')][0]

				nearestTrain_42_local = None
				nearestTime_42_local = None
				arrivalTimes_42_local = [(train.futureStops[u'127N'][0], train) for train in localTrains]
				if len(arrivalTimes_42_local) > 0:
					nearestTime_42_local,nearestTrain_42_local = min(arrivalTimes_42_local)
				startTime_42 = nearestTrain_42_local.futureStops[u'127N'][0] # time the local train I take arriving at 42st

				expressTrains = []
				search = table_dynamo.scan(FilterExpression=(Attr('routeId').eq('2') | Attr('routeId').eq('3')) & Attr('direction').eq('N'))
				trainsDict = search['Items']
				for trainDict in trainsDict:
					train = Incorporation()
					train.constructFromDyDict(trainDict)
					if u'120N' in train.futureStops and u'127N' in train.futureStops:
						expressTrains.append(train)
				if len(expressTrains) == 0:
					print 'no express train stop at 42st, you can take local train and update the app later'
					return 'no express train stop at 42st, you can take local train and update the app later'
				else:
					print 'there are {0} express train to 42st where you can switch'.format(len(expressTrains))

				nearestTrain_42_express = None
				nearestTime_42_express = None
				# available express trains later arriving 42 st than the local train you are on
				arrivalTimes_42_express = [ (train.futureStops[u'127N'][0], train) for train in expressTrains if train.futureStops[u'127N'][0] > startTime_42 ]
				if len(arrivalTimes_42_express) > 0:
					nearestTime_42_express, nearestTrain_42_express = min(arrivalTimes_42_express)
				#duration_express_1 = nearestTime_42_express - startTime_express
				startTime_96 = nearestTrain_42_express.futureStops[u'120N'][0] # time the express train arriving at 96st

				# step 3_2: time for express from 42st to 96st
				#duration_express_2 = nearestTrain_42_express.futureStops[u'120N'][0] - nearestTime_42_express

				# step 3_3: time for whether to change to local again
				if unicode(str(destinationStop) + 'N') in nearestTrain_42_express.futureStops:
					#duration_express_3 = nearestTrain_42_express.futureStops[unicode(str(destinationStop) + 'N')][0] - nearestTrain_42_express.futureStops[u'120S'][0]
					duration_express = (nearestTrain_42_express.futureStops[unicode(str(destinationStop) + 'N')][0] - startTime_express)/60.0
				else:
					nearestTrain_96_local = None
					nearestTime_96_local = None
					arrivalTimes_96_local = [(train.futureStops[u'120N'][0], train) for train in localTrains if train.futureStops[u'120N'][0] > startTime_96]
					if len(arrivalTimes_96_local) > 0:
						nearestTime_96_local, nearestTrain_96_local = min(arrivalTimes_96_local)
					#duration_express_3 = nearestTrain_96_local.futureStops[unicode(str(destinationStop) + 'N')][0] - nearestTime_96_local
					duration_express = (nearestTrain_96_local.futureStops[unicode(str(destinationStop) + 'N')][0] - startTime_express)/60.0

				# step 3_4: add all time together
				# duration_express = (duration_express_1 + duration_express_2 + duration_express_3)/60.0
				print "The time spent with switching to express at 42st is ",duration_express,"min"


				# step 4: make final decision
				if duration_express < duration_local:
					if unicode(str(destinationStop) + 'N') in nearestTrain_96_express.futureStops:
						print "You need to change to the express at 42st to your destination"
						return "You need to change to the express at 42st to your destination"
					else:
						print "You need to change to the express at 42st and change back to local at 96st to your destination"
						return "You need to change to the express at 42st and change back to local at 96st to your destination"

				else:
					print "Stay on your local train is faster"
					return "Stay on your local train is faster"



		else:
			if startStop < destinationStop:
				print "Take the first arrival local train and no need to switch to express"
				return "Take the first arrival local train and no need to switch to express"
			else:
				if 120 < destinationStop < 127:
					print 'Take the first arrival local train and no need to switch to express'
					return 'Take the first arrival local train and no need to switch to express'
				else:
					print 'Take the first train regardless whether it is local or express'
					return 'Take the first train regardless whether it is local or express'


	'''
	# for lcoal line 4 & 6 with express line 5
	see routePlan2.py
	if 401 <= startStop <= 640 and 401 <= destinationStop <= 640:
		
		if 601 <= startStop <= 640 and 601 <= startStop <=640

	'''
if __name__ == "__main__":
	print "input start stop"
	start = input()
	print "input destination stop"
	destination = input()
	routePlan(start,destination)















