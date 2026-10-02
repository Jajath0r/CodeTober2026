import argparse
import csv
import json
from os import path,makedirs

from statistics import increment_status_counter,add_service_statistics,add_to_slowest,get_mean_resp_time

nb_requests = 0
nb_2xx = 0
nb_4xx = 0
nb_5xx = 0
resp_time = 0
services = dict()
top_10_slowest = []

"""ARGUMENTS PARSING"""
parser = argparse.ArgumentParser(
    description="CSV Statistics"
)

parser.add_argument(
    "input",
    type=str,
    help="file to analyze"
)

parser.add_argument(
    "output",
    type=str,
    help="Output repository"
)

args = parser.parse_args()

"""Creation of output filename"""
output_rep = args.output
if not path.exists(output_rep):
    makedirs(output_rep)
report = path.join(output_rep,"report.json")



"""CSV Reading"""
with open(args.input,mode='r',newline="") as api_logs:
    file=csv.DictReader(api_logs)
    for row in file:
        nb_requests += 1
        nb_2xx,nb_4xx,nb_5xx = increment_status_counter(row, nb_2xx,nb_4xx,nb_5xx)
        resp_time += int(row['response_time_ms'])
        services = add_service_statistics(row, services)
        top_10_slowest = add_to_slowest(row, top_10_slowest)

for current_service, values in services.items():
    values['resp_time'] = get_mean_resp_time(values['resp_time'], values['nb_request'])
output_data = {
    "nb_requests_total" : nb_requests,
    "nb_requests_2xx" : nb_2xx,
    "nb_requests_4xx" : nb_4xx,
    "nb_requests_5xx" : nb_5xx,
    "mean_resp_time" : get_mean_resp_time(resp_time,nb_requests),
    "services" : services,
    "top_10_slowest" : top_10_slowest
}

with open(report, 'w') as json_report:
    json.dump(output_data, json_report)