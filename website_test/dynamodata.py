#!/usr/bin/python

# *********************************************************************************************
# Update dynamodb with latest data from mta feed. 
# Use the updated data to make real-time prediction
# *********************************************************************************************
import json,time,sys
from collections import OrderedDict
from threading import Thread

import boto3
from boto3.dynamodb.conditions import Key,Attr

sys.path.append('/Users/shilei/MTA/website_test/utils')
import tripupdate,vehicle,alert,mtaUpdates,aws

import boto
import boto.dynamodb2
from boto.dynamodb2.table import Table

import threading
import time
from datetime import datetime, date

from aws import getResource
from aws import getClient

TIME_INTERVAL_ADD = 30
#ITERATIONS = 100
DYNAMODB_TABLE_NAME = 'mta_'+datetime.today().strftime("%A")

def add_data():
	client = getClient('dynamodb','us-east-1')
	dynamodb = getResource('dynamodb','us-east-1')
	table_dynamo = dynamodb.Table(DYNAMODB_TABLE_NAME)

	print "adding data starts"

	i = 0
	while True:
		newmta = mtaUpdates.mtaUpdates('a39a31d245609da7fc88a7111ab8bfe6')
		tripUpdates = newmta.getTripUpdates()
		j = 0
		for update in tripUpdates:
			table_dynamo.put_item(Item={
				'tripId': str(update.tripId),
				'routeId': str(update.routeId),
				'startDate': str(update.startDate),
				'direction': str(update.direction),
				'futureStops' : str(update.futureStops),
				'timestamp' : str(update.timeStamp),
				'currentStopId' : str(update.currentStopId),
				'currentStopStatus' : str(update.currentStopStatus),
				'vehicleTimeStamp' : str(update.vehicleTimeStamp),
			})
			j = j + 1

		print "I have added data for {0} times".format(i)
		time.sleep(TIME_INTERVAL_ADD)

if __name__ == '__main__':
	client = getClient('dynamodb','us-east-1')
	dynamodb = getResource('dynamodb','us-east-1')
	add_data()



























