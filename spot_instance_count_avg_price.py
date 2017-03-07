# -*- coding: utf-8 -*-
"""
@author: adrzystek
"""

import datetime as dt
import boto3


INSTANCE_TYPE = 'c4.xlarge'
START_TIME = dt.datetime(2016, 6, 10)
AVAILABILITY_ZONE = 'us-west-2a'


client = boto3.client('ec2')

price_list = []
n = 0
break_flg = 0
while(break_flg==0):

    if n == 0:
        response = client.describe_spot_price_history(StartTime=START_TIME, InstanceTypes=[INSTANCE_TYPE], AvailabilityZone=AVAILABILITY_ZONE, ProductDescriptions=['Linux/UNIX'])
    else:
        response = client.describe_spot_price_history(StartTime=START_TIME, InstanceTypes=[INSTANCE_TYPE], AvailabilityZone=AVAILABILITY_ZONE, ProductDescriptions=['Linux/UNIX'], NextToken=next_token)

    next_token = response['NextToken']
    if next_token == '':
        break_flg = 1

    for i in range(len(response['SpotPriceHistory'])):
        price_list.append(float(response['SpotPriceHistory'][i]['SpotPrice']))

    n += 1

print 'AVERAGE PRICE IN THE PERIOD', sum(price_list) / len(price_list)
