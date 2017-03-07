# -*- coding: utf-8 -*-
"""
@author: adrzystek
"""

import boto3
import datetime as dt
import random as rnd


BUCKET_NAME = "results-bucket"
FOLDER_NAME = "fib-lambda_1"

s3 = boto3.client('s3')

def fib(n):
    a, b = 1, 1
    for i in range(n-1):
        a, b = b, a+b
    return a

def fib_handler(event, context):
    file_name = dt.datetime.now().strftime("%Y%m%d%H%M%S%f") + '_' + str(int(rnd.random()*1000)) + '.txt'
    with open("/tmp/"+file_name, "w") as f:
        f.write(str(fib(10000)))
    s3.upload_file("/tmp/"+file_name, BUCKET_NAME, FOLDER_NAME+"/"+file_name)
