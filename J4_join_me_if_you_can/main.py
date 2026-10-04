import argparse
import csv
import json
from os import path,makedirs
from linking import link_order_customer

customers = {}
nb_customers = 0
nb_orders = 0
nb_enriched_orders = 0
nb_unlinked_orders = 0
enriched_amount = 0
unlinked_amount = 0


parser = argparse.ArgumentParser(
    description = "Join two datasets"
)

parser.add_argument(
    "customers_input",
    type=str,
    help="customers file to join"
)

parser.add_argument(
    "orders_input",
    type=str,
    help="orders file to join"
)

parser.add_argument(
    "output",
    type=str,
    help="output repository"
)

args = parser.parse_args()


"""Creation of output files"""
output_rep = args.output
if not path.exists(output_rep):
    makedirs(output_rep)
enriched_orders = path.join(output_rep,"enriched_orders.csv")
unmatched_orders = path.join(output_rep, "unmatched_orders.csv")
customers_without_orders = path.join(output_rep, "customers_without_orders.csv")
join_report = path.join(output_rep, "join_report.json")


with open(args.customers_input, mode="r", newline="") as cust_file:
    r = csv.DictReader(cust_file)
    for row in r:
        customers[row["customer_id"]]={"name":row["name"],"country":row["country"],"segment":row["segment"],"found":False}
        nb_customers += 1

with open(args.orders_input, mode="r", newline="") as orders:
    s = csv.DictReader(orders)
    with open(enriched_orders, mode="w", newline="") as enriched_orders_file:
        enriched_header = s.fieldnames + ["name","country","segment"]
        enriched_w = csv.DictWriter(enriched_orders_file, fieldnames=enriched_header)
        enriched_w.writeheader()
        with open(unmatched_orders, mode="w",newline="") as unmatched_orders_file:
            unlinked_w = csv.DictWriter(unmatched_orders_file, fieldnames=s.fieldnames)
            unlinked_w.writeheader()
            for row in s:
                nb_orders += 1
                if row["customer_id"] in customers:
                    nb_enriched_orders += 1
                    enriched_amount += float(row["amount"])
                    output_row = link_order_customer(customers, row)
                    customers[row["customer_id"]]["found"]=True
                    enriched_w.writerow(output_row)
                else:
                    nb_unlinked_orders += 1
                    unlinked_amount += float(row["amount"])
                    unlinked_w.writerow(row)
nb_customers_without_order = 0
with open(customers_without_orders,"w",newline="") as cust_w_order_file:
    w = csv.DictWriter(cust_w_order_file, fieldnames=r.fieldnames)
    w.writeheader()
    for cust in customers.keys():
        if not customers[cust]["found"]:
            nb_customers_without_order += 1
            customer_output_row = {}
            customer_output_row["customer_id"] = cust
            customer_output_row["name"] = customers[cust]["name"]
            customer_output_row["country"] = customers[cust]["country"]
            customer_output_row["segment"] = customers[cust]["segment"]
            w.writerow(customer_output_row)
    


data = {
    "nombre de clients" : nb_customers,
    "nombre de commandes" : nb_orders,
    "nombre de commandes enrichies" : nb_enriched_orders,
    "nombre de commandes sans client correspondant" : nb_unlinked_orders,
    "nombre de clients sans commande" : nb_customers_without_order,
    "montant total des commandes enrichies" : enriched_amount,
    "montant total des commandes non rapprochées" : unlinked_amount
}

with open(join_report,"w") as report:
    json.dump(data, report)