from typing import Any
from models import Product
from queue import Queue


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

def consume_orders(queue : Queue, catalog : dict[str,Product]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    sales_row_list = []
    rejected_sales_list = []
    while True:
        line = queue.get()
        try:
            if line is None : break
            row = line['row']
            quantity_key = line['quantity_key']
            try:
                sales_row_list.append(create_sales_row(row['product_id'],row,catalog,quantity_key))
            except Exception as e:
                print(f"Erreur : {e} sur la ligne {row}")
                rejected_sales_list.append({"row":row,"error":str(e)})
        finally:
            queue.task_done()
    return sales_row_list, rejected_sales_list