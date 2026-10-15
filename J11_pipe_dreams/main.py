import argparse
from sqlite3 import Connection,connect, Row
from typing import TypedDict, Any
from os import path, makedirs
import csv
import json

class Product(TypedDict):
    name : str
    unit_price_cents : int
    
def parse_input():
    parser = argparse.ArgumentParser(
        description="quality control"
    )
    
    parser.add_argument(
        "input_rep",
        type=str,
        help="path of input files"
    )
    
    return parser.parse_args()

def create_sales_table(connection : Connection) -> None:
    connection.execute(
        "CREATE TABLE IF NOT EXISTS sales (order_id TEXT PRIMARY KEY, order_date TEXT, product_id TEXT, product_name TEXT, quantity INTEGER, unit_price_cents INTEGER, total_cents INTEGER)"
    )

def get_catalog(json_file : str) -> dict[str,Product]:
    with open(json_file) as catalog:
        catalog_dict = json.load(catalog)
    output_dict = {}
    for product in catalog_dict["products"]:
        product_id = product["product_id"]
        output_dict[product_id] = {"name":product["name"],"unit_price_cents":product["unit_price_cents"]}
    return output_dict

def insert_row_in_sales(connection : Connection, row : dict[str,str]) -> None:
    connection.execute(
        "INSERT OR IGNORE INTO sales VALUES (?,?,?,?,?,?,?)",
        (row["order_id"],row["order_date"],row["product_id"],row["product_name"],row["quantity"],row["unit_price_cents"],row["total_cents"])
    )
    
def create_sales_row(id_product : str, row : dict[str,str], catalog : dict[str,Product]) -> dict[str,Any]:
    sales_row = {}
    sales_row["order_id"] = row["order_id"]
    sales_row["order_date"] = row["order_date"]
    sales_row["product_id"] = row["product_id"]
    sales_row["quantity"] = int(row["quantity"])
    sales_row["product_name"] = catalog[id_product]["name"]
    sales_row["unit_price_cents"] = int(catalog[id_product]["unit_price_cents"])
    sales_row["total_cents"] = int(catalog[id_product]["unit_price_cents"]) * int(row["quantity"])
    return sales_row

def main():
    args = parse_input()
    input_rep = args.input_rep
    connection = connect('sales.db')
    connection.row_factory = Row
    create_sales_table(connection)
    json_input = path.join(input_rep,"catalog.json")
    catalog = get_catalog(json_input)
    orders_file = path.join(input_rep,"orders.csv")
    with open(orders_file,'r',newline="") as orders:
        r = csv.DictReader(orders)
        for row in r:
            if row["status"] == "paid":
                id_product = row['product_id']
                if id_product in catalog:
                    sales_row = create_sales_row(id_product,row,catalog)
                    insert_row_in_sales(connection, sales_row)
        connection.commit()
if __name__ == "__main__":
    main()