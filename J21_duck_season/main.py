import duckdb
import argparse
from os import path,makedirs
from extract import extract_order_items, extract_orders, extract_products
from transform import transform_category_sales,transform_daily_sales,transform_top_products
from load import load_category_sales,load_daily_sales,load_top_products

def parse_input():
    parser = argparse.ArgumentParser(
        description="Duck Season"
    )

    parser.add_argument(
        "--data-dir",
        type=str,
        required=True,
        help="Directory containing input datasets"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Directory for generated reports"
    )

    return parser.parse_args()

def main():
    args = parse_input()
    data_dir = args.data_dir
    output_dir = args.output_dir
    if not path.exists(output_dir):
        makedirs(output_dir)
    connection = duckdb.connect(":memory:")
    extract_orders(connection, data_dir)
    extract_order_items(connection, data_dir)
    extract_products(connection, data_dir)
    transform_top_products(connection)
    transform_daily_sales(connection)
    transform_category_sales(connection)
    load_top_products(output_dir,connection)
    load_daily_sales(output_dir,connection)
    load_category_sales(output_dir,connection)
if __name__ == "__main__":
    main()