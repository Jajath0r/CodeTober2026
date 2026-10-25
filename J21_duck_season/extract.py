import duckdb
from os import path

def extract_orders(connection : duckdb.DuckDBPyConnection, input_repository : str) -> None:
    orders_file_path = path.join(input_repository, "orders.csv")
    connection.read_csv(orders_file_path).create_view("orders")

def extract_order_items(connection : duckdb.DuckDBPyConnection, input_repository : str) -> None:
    items_file_path = path.join(input_repository, "order_items.csv")
    connection.read_csv(items_file_path).create_view("items")

def extract_products(connection : duckdb.DuckDBPyConnection, input_repository : str) -> None:
    product_file_path = path.join(input_repository, "products.csv")
    connection.read_csv(product_file_path).create_view("products")