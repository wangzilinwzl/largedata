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

import tripupdate
import vehicle
import alert
import mtaUpdates
import aws

import boto
import boto.dynamodb2
from boto.dynamodb2.table import Table
from botocore.exceptions import ClientError

import threading
import time

from aws import getResource
from aws import getClient

TIME_INTERVAL_ADD = 80
DYNAMODB_TABLE_NAME = 'Alert1'


def add_data():
    client = getClient('dynamodb', 'us-east-1')
    dynamodb = getResource('dynamodb', 'us-east-1')
    table_dynamo = dynamodb.Table(DYNAMODB_TABLE_NAME)

    print "adding data starts"

    cnt = 0
    batch = 0
    while True:
        batch += 1
        newmta = mtaUpdates.mtaUpdates('a39a31d245609da7fc88a7111ab8bfe6')
        tripUpdates = newmta.getTripUpdates()
        for update in tripUpdates:
            cnt += 1
            try:
                table_dynamo.put_item(Item={
                    'uid': str(cnt),
                    'batch': batch,
                    'tripId': str(update.tripId),
                    'routeId': str(update.routeId),
                    'startDate': str(update.startDate),
                    'direction': str(update.direction),
                    'futureStops' : str(update.futureStops),
                    'timestamp' : str(update.timeStamp),
                    'currentStopId' : str(update.currentStopId),
                    'currentStopStatus' : str(update.currentStopStatus),
                    'vehicleTimeStamp' : str(update.vehicleTimeStamp),
                    'alert' : str(update.alert)
                })
            except ClientError as e:
                print e.response['Error']['Message']
                print cnt
                print str(update.tripId)
                print str(update.routeId)
                print str(update.startDate)
                print str(update.direction)
                print str(update.futureStops)
                print str(update.timeStamp)
                print str(update.currentStopId)
                print str(update.currentStopStatus)
                print str(update.vehicleTimeStamp)
                print str(update.alert)


        if batch % 40 == 0:
            client = getClient('dynamodb', 'us-east-1')
            dynamodb = getResource('dynamodb', 'us-east-1')
            table_dynamo = dynamodb.Table(DYNAMODB_TABLE_NAME)

        time.sleep(TIME_INTERVAL_ADD)



if __name__ == '__main__':

    t_add = threading.Thread(target = add_data)
    t_add.setDaemon(True)
    t_add.start()

    while True:
        time.sleep(5)




























