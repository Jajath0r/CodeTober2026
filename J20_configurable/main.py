import argparse
from sqlite3 import connect,Row
from os import path,makedirs
from extract import get_catalog
from load import create_catalog_table, insert_product_in_catalog,create_logging_table, insert_logging
from time import perf_counter
import datetime
import sys

def parse_input():
    parser = argparse.ArgumentParser(
        description="Slowly but surely"
    )
    
    parser.add_argument(
        "input_rep",
        type=str,
        help="catalog repository path"
    )
    
    parser.add_argument(
        "input_file",
        type=str,
        help="catalog filename"
    )
    parser.add_argument(
        "output_rep",
        type=str,
        help="output repository"
    )
    
    return parser.parse_args()


def main():
    args = parse_input()
    start = perf_counter()
    output_rep = args.output_rep
    if not path.exists(output_rep):
        makedirs(output_rep)
    db_path = path.join(output_rep,"catalog.db")
    connection = connect(db_path)
    connection.row_factory = Row
    input_rep = args.input_rep
    catalog = args.input_file
    catalog_date = catalog[8:18]
    catalog_path = path.join(input_rep, catalog)
    nb_processed_lines = 0
    nb_inserted_lines = 0
    start_time = datetime.datetime.now()
    exec_id = catalog.removesuffix(".json") + "_" + str(start_time.timestamp())
    steps = []
    try:
        catalog_dict = get_catalog(catalog_path)
        steps.append("EXTRACT")
        create_catalog_table(connection)
        steps.append("INIT_DB")
        for product_id, product in catalog_dict.items():
            row = {"product_id": product_id, **product}
            nb_inserted_lines += insert_product_in_catalog(connection, row, catalog_date)
            nb_processed_lines += 1
        steps.append("LOAD")
        connection.commit()
        steps.append("COMMIT")
    except Exception as e:
        connection.rollback()
        error_type = type(e).__name__
        nb_inserted_lines = 0
        status="FAILED"
        raise
    else:
        error_type = None
        status = "SUCCESS"
    finally:
        connection.close()
        connection = connect(db_path)
        connection.row_factory = Row
        try:
            create_logging_table(connection)
            insert_logging(connection,exec_id,catalog_path, catalog_date, status, error_type, ", ".join(steps),nb_processed_lines, nb_inserted_lines, start)
            connection.commit()
        except Exception as e:
            connection.rollback()
            if status == "FAILED":
                print(f"Logging failed: {type(e).__name__}", file=sys.stderr)
            else:   
                raise
        finally:
            connection.close()
        
if __name__ == "__main__":
    main()