import argparse
from datetime import datetime
from sqlite3 import Connection, connect, Row
import csv
import json
from os import path, makedirs
import collections
from typing import Any

def parse_input():
    parser = argparse.ArgumentParser(
        description="upsert or shut up"
    )
    
    parser.add_argument(
        "input_csv",
        type=str,
        help="input csv file"
    )
    
    parser.add_argument(
        "batch",
        type=str,
        help="batch id"
    )
    
    parser.add_argument(
        "database_path",
        type=str,
        help="path to sqlite"
    )
    
    parser.add_argument(
        "output_rep",
        type=str,
        help="output repository"
    )
    return parser.parse_args()

def create_sql_tables(connection : Connection) -> None:
    connection.execute(
        "CREATE TABLE IF NOT EXISTS customers (customer_id TEXT PRIMARY KEY, full_name TEXT, email TEXT, country TEXT, updated_at TEXT)"
    )
    connection.commit()
    
def return_timestamp_if_valid(timestamp : str) -> datetime | None:
    try:
        current_timestamp = datetime.strptime(timestamp,"%Y-%m-%dT%H:%M:%S")
        return current_timestamp
    except ValueError:
        return None

def insert_customer(connection : Connection, row : dict[str,str], report_dict : dict[str,Any]) -> None:
    customer_id = row["customer_id"]
    full_name = row["full_name"]
    email = row["email"]
    country = row["country"]
    timestamp = return_timestamp_if_valid(row["updated_at"])
    report_dict["nb_read"] += 1
    if customer_id == "" or full_name == "" or email == "" or country == "" or timestamp is None:
        report_dict["nb_rejected"] += 1
        return
    current_customer = get_existing_customers(connection,customer_id)
    if current_customer == None:
        connection.execute(
            "INSERT INTO customers VALUES (?,?,?,?,?)",(row["customer_id"],row["full_name"],row["email"],row["country"],return_timestamp_if_valid(row["updated_at"]))
        )
        report_dict["nb_inserted"] += 1
    elif return_timestamp_if_valid(current_customer["updated_at"])< timestamp:
        connection.execute("UPDATE customers SET full_name = ?, email = ?, country = ?, updated_at = ? WHERE customer_id = ?", (full_name, email, country, timestamp, customer_id))
        report_dict["nb_updated"] += 1
    else:
        if current_customer["full_name"] == full_name and current_customer["email"] == email and current_customer["country"] == country:
            if return_timestamp_if_valid(current_customer["updated_at"]) == timestamp:
                report_dict["nb_unchanged"] += 1
            elif return_timestamp_if_valid(current_customer["updated_at"]) > timestamp:
                report_dict["nb_rejected"] += 1
            else:
                report_dict["nb_conflict"] += 1

def get_existing_customers(connection : Connection, customer_id : str) -> Row | None:
    customer = connection.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,)).fetchone()
    return customer

def get_all_customers(connection : Connection): 
    customers = {
        customer["customer_id"]: {"full_name" : customer["full_name"], "email" : customer["email"], "country" : customer["country"], "updated_at" : customer["updated_at"]}
        for customer in connection.execute("SELECT * FROM customers")
    }
    return customers
    
    
def main():
    args = parse_input()
    input_batch = args.batch
    database_path = args.database_path
    output_rep = args.output_rep
    report_dict = {
        "batch" : args.batch,
        "nb_read" : 0,
        "nb_inserted" : 0,
        "nb_updated" : 0,
        "nb_unchanged" : 0,
        "nb_conflict" : 0,
        "nb_rejected" : 0,
        "nb_customers_after" :0
    }
    if not path.exists(output_rep):
        makedirs(output_rep)
    input_csv = args.input_csv+"_"+args.batch+".csv"
    output_json = path.join(output_rep, "report.json")
    snapshot = path.join(output_rep,"customers_snapshot.csv")
    connection = connect(database_path)
    connection.row_factory = Row
    create_sql_tables(connection)
    with open(input_csv, "r", newline = "") as csv_in:
        r = csv.DictReader(csv_in)
        for row in r:
            insert_customer(connection, row, report_dict)
    connection.commit()
    final_customers = get_all_customers(connection)
    ordered_customers = collections.OrderedDict(sorted(final_customers.items()))
    with open(snapshot,"w",newline="") as snap:
        w = csv.DictWriter(snap, fieldnames=r.fieldnames)
        w.writeheader()
        for k,v in ordered_customers.items():
            row = {}
            row["customer_id"] = k
            report_dict["nb_customers_after"] += 1
            for key in v.keys():
                row[key] = v[key]
            w.writerow(row)
    with open(output_json,"w") as report:
        json.dump(report_dict,report)

if __name__ == "__main__":
    main()