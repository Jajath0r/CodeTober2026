import argparse
import duckdb
from extract import extract_sales
from validation import validate_sales_input_schema,validate_sales_data,validate_input_arguments
from transform import transform_sales_data, transform_monthly_summary,transform_selected_sales
from load import load_parquet, load_monthly_summary, load_selected_sales

def parse_input():
    parser = argparse.ArgumentParser(
        description="Duck Season"
    )

    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input dataset file"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Directory for generated reports"
    )

    parser.add_argument(
        "--month",
        type=str,
        required=True,
        help="Month with format YYYY-MM"
    )

    parser.add_argument(
        "--country",
        type=str,
        required=True,
        help="2 char Country code like 'FR'"
    )        

    return parser.parse_args()


def main():
    args = parse_input()
    input_file = args.input
    validate_input_arguments(args)
    connection = duckdb.connect(":memory:")
    
    
    # EXTRACT
    extract_sales(connection,input_file)
    
    validate_sales_input_schema(connection)
    validate_sales_data(connection)
    
    # TRANSFORM
    transform_sales_data(connection)
    transform_monthly_summary(connection)

    load_parquet(connection, args.output_dir)

    transform_selected_sales(connection, args.output_dir, args.month, args.country)

    load_monthly_summary(connection, args.output_dir)
    load_selected_sales(connection, args.output_dir)
    

if __name__ == "__main__":
    main()