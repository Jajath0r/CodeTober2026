from models import Product
from simulator import SimulatedCatalogSource, TransientSourceError
from typing import Any
from queue import Queue
import time
import csv
    

def get_catalog(source: SimulatedCatalogSource) -> dict[str,Product]:
    catalog_data = fetch_catalog(source)  # objet JSON décodé : {"products": [...]}
    output_dict = {}
    for product in catalog_data["products"]:
        product_id = product["product_id"]
        output_dict[product_id] = {"name":product["name"],"unit_price_cents":product["unit_price_cents"]}
    return output_dict


def fetch_catalog(source : SimulatedCatalogSource, sleep_func = time.sleep) -> dict[str, Any]:
    attempts = 0
    delay = 0.5
    while attempts < 3:
        try:
            catalog_data = source.fetch()
        except TransientSourceError:
            attempts += 1
            if attempts == 3:
                raise
            sleep_func(delay)
            delay = min(delay + 0.5, 1)
        else:
            return catalog_data
        
def validate_input_schema(file_fieldnames : set[str]) -> str:
    compulsory_fields = {"order_id","order_date","product_id","status"}
    quantity_options = {"quantity", "units", "items_count"}
    missing_fields = compulsory_fields - file_fieldnames
    if missing_fields:
        raise ValueError(f"Missing required columns : {missing_fields}")
    quantity_columns = file_fieldnames & quantity_options
    if len(quantity_columns) != 1:
        raise ValueError("Expected exactly one quantity column")
    return quantity_columns.pop()
        
def produce_orders(order_file : str, sales_queue : Queue):
    with open(order_file, "r", newline="") as orders:
        r = csv.DictReader(orders)
        quantity_key = validate_input_schema(set(r.fieldnames or []))
        for row in r:
            line = {
                "row":row,
                "quantity_key":quantity_key
            }
            sales_queue.put(line)
