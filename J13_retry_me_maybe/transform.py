from typing import Any
from models import Product


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

def create_sales_row(id_product : str, row : dict[str,str], catalog : dict[str,Product], quantity_key : str) -> dict[str,Any]:
    sales_row = {}
    quantity = int(row[quantity_key])
    sales_row["order_id"] = row["order_id"]
    sales_row["order_date"] = row["order_date"]
    sales_row["product_id"] = row["product_id"]
    sales_row["quantity"] = quantity
    sales_row["product_name"] = catalog[id_product]["name"]
    sales_row["unit_price_cents"] = int(catalog[id_product]["unit_price_cents"])
    sales_row["total_cents"] = int(catalog[id_product]["unit_price_cents"]) * quantity
    return sales_row