from validations import get_error_list, increment_event_type_dict
import argparse
import csv
import json
from os import path, makedirs

nb_events = 0
nb_valid = 0
nb_reject = 0
event_type_dict = {"order_created" : 0, "payment_received" : 0, "customer_updated" : 0}
error_dict = {}

"""PARSING"""
parser = argparse.ArgumentParser(
    description="Schema says no"
)

parser.add_argument(
    "input",
    type=str,
    help="File to analyze"
)

parser.add_argument(
    "output",
    type=str,
    help="output repository"
)

args = parser.parse_args()

"""Création des noms de fichier de sortie"""
output_rep = args.output
if not path.exists(output_rep):
    makedirs(output_rep)
valid_events = path.join(output_rep, "valid_events.csv")
rejected_events = path.join(output_rep, "rejected_events.csv")
validation_report = path.join(output_rep, "validation_report.json")


"""Lecture CSV"""
with open(args.input, mode='r', newline='') as input_file:
    r=csv.DictReader(input_file)
    header = r.fieldnames
    with open(valid_events, mode='w', newline="") as valid_output:
        w_valid = csv.DictWriter(valid_output, fieldnames=header)
        with open(rejected_events, mode="w", newline="") as rejected_output:
            reject_header = header + ["validation_errors"]
            w_reject = csv.DictWriter(rejected_output, fieldnames = reject_header)
            for row in r:
                nb_events += 1
                rejects = get_error_list(row)
                if len(rejects) > 0:
                    row["validation_errors"] = ", ".join(rejects)
                    w_reject.writerow(row)
                    nb_reject += 1
                    for error_type in rejects:
                        if error_type not in error_dict.keys():
                            error_dict[error_type] = 1
                        else:
                            error_dict[error_type] +=1
                else:
                    nb_valid += 1
                    w_valid.writerow(row)
                event_type_dict = increment_event_type_dict(row, event_type_dict)



validation_report_data = {
    "nombre total d'évènements" : nb_events,
    "nombre d'évènements valides" : nb_valid,
    "nombre d'événements rejetés" : nb_reject,
    "nombre d'événements par `event_type`" : event_type_dict,
    "nombre d'erreurs par règle ou champ" : error_dict
}
with open(validation_report,"w") as validation_report_json:
    json.dump(validation_report_data, validation_report_json)