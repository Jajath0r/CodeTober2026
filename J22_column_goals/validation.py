from argparse import Namespace
from os import path, makedirs
import duckdb
from models import StatusType
import pycountry
from datetime import datetime

def validate_sales_input_schema(connection : duckdb.DuckDBPyConnection) -> None:
    expected_columns = ["transaction_id","order_date","country","product_id","status","quantity","unit_price_cents"]
    columns = [c[0] for c in connection.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'sales'
    """).fetchall()]
    for c in expected_columns:
        if c not in columns:
            raise ValueError(f"Missing required column: {c}")

def validate_sales_data(connection : duckdb.DuckDBPyConnection) -> None:
    column_type_dict = {
        "transaction_id" : "VARCHAR",
        "order_date" : "DATE",
        "country" : "VARCHAR",
        "product_id" : "VARCHAR",
        "status" : "VARCHAR",
        "quantity" : "INTEGER",
        "unit_price_cents" : "INTEGER"
    }
    for column, column_type in column_type_dict.items():
        validate_not_null_value_type(connection,column, column_type)
    validate_country_code(connection)
    validate_status(connection)

def validate_not_null_value_type(connection : duckdb.DuckDBPyConnection, column : str, column_type : str) -> None:
    query = f"""
        SELECT COUNT(*)
        FROM sales
        WHERE TRY_CAST("{column}" AS {column_type}) IS NULL
    """

    if column_type == "VARCHAR":
        query += f"""
            OR TRIM("{column}") = ''
        """
    invalid_count = connection.execute(query).fetchone()[0]
    if invalid_count > 0:
        raise ValueError(
            f"{invalid_count} invalid values in column {column}"
        )

def validate_country_code(connection: duckdb.DuckDBPyConnection) -> None:
    query = f"""
        SELECT DISTINCT country
        FROM sales
    """
    pays_list = [t[0] for t in connection.execute(query).fetchall()]
    for pays in pays_list:
        if len(pays)!=2 or pays.upper()!=pays or pycountry.countries.get(alpha_2=pays) is None:
            raise ValueError(f"Invalid country code {pays}")
        
def validate_status(connection : duckdb.DuckDBPyConnection) -> None:
    query = f"""
        SELECT DISTINCT status
        FROM sales
    """
    status_list = [t[0] for t in connection.execute(query).fetchall()]
    for status in status_list:
        try:
            StatusType(status)
        except ValueError as e:
            raise ValueError(f"Invalid status: {status}") from e


def validate_input_arguments(args : Namespace) -> None:
    output_dir = args.output_dir
    order_month = args.month
    country = args.country
    if not path.exists(output_dir):
        makedirs(output_dir)
    if len(country)!=2 or country.upper()!=country or pycountry.countries.get(alpha_2=country) is None:
        raise ValueError(f"Invalid country code {country}")
    try:
        datetime.strptime(order_month, "%Y-%m")
    except ValueError as e:
        raise ValueError(f"Wrong month input {order_month}")from e