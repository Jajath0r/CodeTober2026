import argparse
from os import path, makedirs
import csv
import json
from sqlite3 import Connection, connect, Row
from datetime import datetime
from contextlib import ExitStack
from typing import Sequence

def parse_input():
    parser = argparse.ArgumentParser(
        description="quality control"
    )
    
    parser.add_argument(
        "input_rep",
        type=str,
        help="path of input files"
    )
    
    parser.add_argument(
        "batch",
        type=str,
        help="batch id"
    )
    
    parser.add_argument(
        "output_rep",
        type=str,
        help="output repository"
    )
    return parser.parse_args()

def create_tables(connection: Connection):
    connection.execute(
        "CREATE TABLE IF NOT EXISTS customers (customer_id TEXT PRIMARY KEY, status TEXT)"
        )
    connection.commit()
    connection.execute(
        "CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY AUTOINCREMENT, batch_id TEXT,order_id TEXT,customer_id TEXT,order_date TEXT,quantity INTEGER,unit_price_cents INTEGER,currency TEXT, is_valid INTEGER, error_code TEXT)"
    )
    connection.execute(
        "DELETE FROM audit"
    )
    connection.execute(
        "DELETE FROM customers"
    )
    connection.commit()

def insert_all_customers(connection : Connection, reader : csv.DictReader):
    for row in reader:
        connection.execute(
            "INSERT OR IGNORE INTO customers VALUES (?,?)",
            (row["customer_id"], row["status"])
        )
    connection.commit()
    
def insert_in_audit(connection : Connection, row : dict[str,str], is_valid_row : int, error_code : list[str]) -> None:
    error_codes = ", ".join(error_code)
    connection.execute(
        """
        INSERT INTO audit (
            batch_id, order_id, customer_id, order_date,
            quantity, unit_price_cents, currency,
            is_valid, error_code
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            row["batch_id"],
            row["order_id"],
            row["customer_id"],
            row["order_date"],
            row["quantity"],
            row["unit_price_cents"],
            row["currency"],
            is_valid_row,
            error_codes
        )
    )

def return_timestamp_if_correct(timestamp : str) -> datetime | None:
    try:
        return datetime.strptime(timestamp,"%Y-%m-%d")
    except ValueError:
        return None

def add_errors_to_dict(error_dict : dict[str,int], error_codes : list[str]) -> None:
    for error in error_codes:
        if error in error_dict:
            error_dict[error] += 1
        else:
            error_dict[error] = 1

def validate_row(error_dict : dict[str,int],row : dict[str,str], connection: Connection, accepted_currencies : set[str], desired_batch : str, order_ids : set[str], customers : dict[str,str]) -> None:
    error_codes = []
    timestamp = return_timestamp_if_correct(row["order_date"])
    order_id = row["order_id"]
    customer_id = row["customer_id"]
    if row['batch_id'] == "":
        error_codes.append("MISSING_BATCH_ID")
    elif row['batch_id'] != desired_batch:
        return
    if order_id == "":
        error_codes.append("MISSING_ORDER_ID")
    elif order_id in order_ids:
        error_codes.append("DUPLICATE_ORDER_ID")
    if customer_id == "":
        error_codes.append("MISSING_CUSTOMER_ID")
    elif customer_id not in customers:
        error_codes.append("UNKNOWN_CUSTOMER")
    elif customers[customer_id] != 'active':
        error_codes.append("INACTIVE_CUSTOMER")
    if timestamp is None:
        error_codes.append("INVALID_ORDER_TIMESTAMP")
    elif timestamp.strftime("%Y-%m") != "2026-10":
        error_codes.append("WRONG_ORDER_DATE")
    try:
        quantity = int(row["quantity"])
        if quantity <= 0:
            error_codes.append("INVALID_QUANTITY")
    except ValueError:
        error_codes.append("INVALID_QUANTITY")
    try:
        price = int(row["unit_price_cents"])
        if price < 0:
            error_codes.append("INVALID_PRICE")
    except ValueError:
        error_codes.append("INVALID_PRICE")
    if row["currency"] not in accepted_currencies:
        error_codes.append("INVALID_CURRENCY")
    add_errors_to_dict(error_dict,error_codes)
    if error_codes:
        insert_in_audit(connection, row, 0, error_codes)
    else:
        order_ids.add(order_id)
        insert_in_audit(connection, row, 1, error_codes)      
    
        
def get_all_customers(connection : Connection) -> set[str]:
    customers =  {
        customer[0] : customer[1]
        for customer in connection.execute("SELECT * FROM customers")
    }
    return customers


def validate_required_columns(required_columns : list[str], fieldnames : list[str] | None):
    missing_columns = []
    for col in required_columns:
        if col not in (fieldnames or []):
            missing_columns.append(col)
    if missing_columns:
        colonnes = ", ".join(missing_columns)
        raise ValueError(f"Missing required columns: {colonnes}")

def get_all_lines_from_query(connection : Connection, query : str):
    orders = connection.execute(query).fetchall()
    lines = []
    for order in orders:
        order = dict(order)
        lines.append(order)
    return lines

def write_output_file(output_file : str, row_list : list[dict[str,str]], stack : ExitStack, fieldnames : Sequence[str] | None) -> None:
    orders = stack.enter_context(
        open(output_file,"w",newline="")
    )
    w = csv.DictWriter(orders, fieldnames=fieldnames)
    w.writeheader()
    for line in row_list:
        row = {k: line[k] for k in fieldnames if k in line}
        w.writerow(row)

def write_rejected_batches(rejected_batches_file : str, stack : ExitStack, batch_ratio : float, batch : str)-> None:
    rejected_batches = stack.enter_context(
        open(rejected_batches_file,"a",newline="")
    )
    header = ["batch_id","ratio"]
    sniffer = csv.Sniffer()
    w = csv.DictWriter(rejected_batches,fieldnames=header)
    if not sniffer.has_header(rejected_batches.read(2048)):
        w.writeheader()
    w.writerow({"batch_id":batch,"ratio":batch_ratio})

def main():
    args = parse_input()
    input_rep = args.input_rep
    output_rep = args.output_rep
    batch = args.batch
    if not path.exists(output_rep):
        makedirs(output_rep)
    if not path.exists(input_rep):
        print("ERROR : input repository does not exist !")
        return
    orders_file = path.join(input_rep,"orders.csv")
    customers_file = path.join(input_rep,"customers.csv")
    quality_file = path.join(input_rep,"quality_config.json")
    accepted_orders_file = path.join(output_rep,"accepted_orders.csv")
    quarantine_file = path.join(output_rep,"quarantine.csv")
    rejected_batches_file = path.join(output_rep,"rejected_batches.csv")
    quality_report_file = path.join(output_rep,"quality_report.json")
    database_path = "quality_db.db"
    order_ids = set()
    connection = connect(database_path)
    connection.row_factory = Row
    error_dict = {}
    create_tables(connection)
    with open(customers_file, "r", newline="") as cust:
        c = csv.DictReader(cust)
        insert_all_customers(connection, c)
    customers = get_all_customers(connection)
    with open(quality_file) as quality:
        quality_dict = json.load(quality)
    with open(orders_file, "r", newline="") as orders:
        r = csv.DictReader(orders)
        required_fieldnames = quality_dict['required_columns']
        accepted_currencies = set(quality_dict['accepted_currencies'])
        validate_required_columns(required_fieldnames, r.fieldnames)
        for row in r:
            validate_row(error_dict, row, connection, accepted_currencies, batch, order_ids, customers)
        connection.commit()
    batch_lines = get_all_lines_from_query(connection,"SELECT * FROM audit")
    nb_lines = len(batch_lines)
    valid_lines = get_all_lines_from_query(connection,"SELECT * FROM audit WHERE is_valid = 1")
    invalid_lines = get_all_lines_from_query(connection,"SELECT * FROM audit WHERE is_valid = 0")
    nb_invalid_lines = len(invalid_lines)
    if nb_lines > 0:
        batch_ratio = nb_invalid_lines/nb_lines
    else:
        batch_ratio = 1.0
    report_dict = {
        "batch_id" : batch,
        "nb_lines" : nb_lines,
        "nb_valid_lines" : len(valid_lines),
        "nb_invalid_lines" : nb_invalid_lines,
        "invlidity_rate" : batch_ratio,
        "error_dict" : error_dict
    }
    with ExitStack() as stack:
        if batch_ratio <= quality_dict["max_invalid_ratio"]:
            write_output_file(accepted_orders_file,valid_lines,stack,r.fieldnames)
            write_output_file(quarantine_file,invalid_lines,stack,r.fieldnames+['error_code'])
        else:
            write_rejected_batches(rejected_batches_file,stack,batch_ratio,batch)
        quality_report = stack.enter_context(
            open(quality_report_file,"w")
        )
        json.dump(report_dict,quality_report)
    
    
            

if __name__ == "__main__":
    main()