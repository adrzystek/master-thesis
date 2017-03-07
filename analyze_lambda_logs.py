# -*- coding: utf-8 -*-
"""
@author: adrzystek
"""

import re
import boto3


FUNCTION_NAME = 'fib_function_1'
FUNCTION_MEMORY_ALLOCATION = 128

logs_client = boto3.client('logs')

compute_time = 0
number_of_requests = 0
all_bills = []
n = 0
break_flg = 0
billed_times_freq = {}

while (break_flg==0):

    if n == 0:
        describe_log_streams_response = logs_client.describe_log_streams(logGroupName='/aws/lambda/'+FUNCTION_NAME)
    else:
        describe_log_streams_response = logs_client.describe_log_streams(logGroupName='/aws/lambda/'+FUNCTION_NAME, nextToken=next_log_streams_token)

    try:
        next_log_streams_token = describe_log_streams_response['nextToken']
    except:
        break_flg = 1

    streams = re.findall("u'logStreamName': u'(.*?)'", str(describe_log_streams_response))

    for stream in streams:
        m = 0
        while (True):
            if m == 0:
                get_log_events_response = logs_client.get_log_events(logGroupName='/aws/lambda/'+FUNCTION_NAME, logStreamName=stream)
            else:
                get_log_events_response = logs_client.get_log_events(logGroupName='/aws/lambda/'+FUNCTION_NAME, logStreamName=stream, nextToken=next_log_events_token)
            if get_log_events_response['events'] == []:
                break
            next_log_events_token = get_log_events_response['nextBackwardToken']
            billed_duration_list = re.findall('Billed Duration: (.*?) ms', str(get_log_events_response))
            try:
                avg_billed_time = sum([int(i)/1000. for i in billed_duration_list]) / float(len(billed_duration_list))
                all_bills.append(avg_billed_time)
            except Exception as e:
                print 'Exception:', e
            for i in billed_duration_list:
                billed_times_freq[i] = billed_times_freq.get(i, 0) + 1
            compute_time += sum([int(i)/1000. for i in billed_duration_list])
            number_of_requests += len(billed_duration_list)
            m += 1
        n += 1

compute_charge = compute_time * 0.00001667 * FUNCTION_MEMORY_ALLOCATION / 1024
request_charge = number_of_requests * 0.0000002

print 'NUMBER OF REQUESTS:   ', number_of_requests
print 'TOTAL CHARGE:   ', compute_charge + request_charge
print 'AVERAGE BILLED TIME [SECONDS]:   ', sum(all_bills) / float(len(all_bills))
print 'BILLED TIME DISTRIBUTION:   ', billed_times_freq
