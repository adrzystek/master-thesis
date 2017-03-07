# -*- coding: utf-8 -*-
"""
@author: adrzystek
"""

import numpy
import boto.utils
import boto3
import datetime as dt
import random as rnd
import timeit
import pickle


NUMBER_OF_PROCESSES = 4
BUCKET_NAME = "results-bucket"

intance_id = boto.utils.get_instance_metadata()['instance-id']

s3 = boto3.client('s3')

def randmatmul(size):
    A = numpy.random.rand(size, size)
    B = numpy.random.rand(size, size)
    return str(numpy.dot(A,B))

def randmatmul_run():
    file_name = dt.datetime.now().strftime("%Y%m%d%H%M%S%f") + '_' + str(int(rnd.random()*1000)) + '.txt'
    with open(file_name, "w") as f:
        f.write(randmatmul(1000))
    s3.upload_file(file_name, BUCKET_NAME, "randmatmul_"+str(NUMBER_OF_PROCESSES)+"/"+intance_id+"/"+file_name)

exec_times = timeit.repeat("randmatmul_run()", setup="from __main__ import randmatmul_run", repeat=1000, number=1)
final_file_name = "randmatmul_"+str(NUMBER_OF_PROCESSES)+"_times_"+intance_id+"_"+str(int(rnd.random()*1000))+".txt"
with open(final_file_name, "wb") as ff:
    pickle.dump(exec_times, ff)

s3.upload_file(final_file_name, BUCKET_NAME, "results/"+final_file_name)
