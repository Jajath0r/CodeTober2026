import duckdb
from os import path

def extract_sales(connection : duckdb.DuckDBPyConnection, input_file : str) -> None:
    connection.read_csv(input_file).create_view("sales")
