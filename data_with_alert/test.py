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

# sys.path.append('../utils')
import tripupdate
import vehicle
import alert
import mtaUpdates
import aws

import boto
import boto.dynamodb2
from boto.dynamodb2.table import Table

import threading
import time

from aws import getResource
from aws import getClient

TIME_INTERVAL_ADD = 5


def add_data():

    print "adding data starts"
    cnt = 0
    print cnt
    while True:
        cnt += 1
        print str(cnt)
        newmta = mtaUpdates.mtaUpdates('a39a31d245609da7fc88a7111ab8bfe6')
        tripUpdates = newmta.getTripUpdates()
        for update in tripUpdates:
            if update.tripId == "011850_4..N06X055":
                print str(update.alert)
                print str(update.vehicleTimeStamp)
        time.sleep(TIME_INTERVAL_ADD)


if __name__ == '__main__':

    t_add = threading.Thread(target = add_data)
    t_add.setDaemon(True)
    t_add.start()

    while True:
        time.sleep(5)




























