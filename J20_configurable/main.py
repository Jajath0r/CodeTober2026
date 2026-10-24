import argparse
from sqlite3 import connect,Row
from os import makedirs, path
from extract import get_catalog, get_configuration_data, get_source_file, get_destination_file, get_invalid_product_behavior
from load import create_catalog_table, insert_product_in_catalog,create_logging_table, insert_logging
from models import InvalidProductBehavior,InvalidProductError
from time import perf_counter
import datetime
from datetime import date
import sys

def parse_input():
    parser = argparse.ArgumentParser(
        description="Configurable"
    )
    parser.add_argument(
        "input_json",
        type=str,
        help="configuration file path"
    )
    
    return parser.parse_args()


def main():
    args = parse_input()
    start = perf_counter()
    input_json = args.input_json
    config_path = path.abspath(input_json)
    config_dir = path.dirname(config_path)
    configuration_dict = get_configuration_data(input_json)
    source_path = get_source_file(config_dir, configuration_dict)
    catalog = path.basename(source_path)
    catalog_date = catalog.removeprefix("catalog_")[:10]
    catalog_date = date.fromisoformat(catalog_date).isoformat()
    destination_path = get_destination_file(config_dir, configuration_dict)
    invalid_behavior = get_invalid_product_behavior(configuration_dict)
    if not path.isfile(source_path):
        raise ValueError(f"Source {source_path} does not exist")
    if not path.exists(path.dirname(destination_path)):
        makedirs(path.dirname(destination_path))
    connection = connect(destination_path)
    connection.row_factory = Row
    nb_processed_lines = 0
    nb_inserted_lines = 0
    start_time = datetime.datetime.now()
    exec_id = catalog.removesuffix(".json") + "_" + str(start_time.timestamp())
    steps = []
    try:
        catalog_dict = get_catalog(source_path)
        steps.append("EXTRACT")
        create_catalog_table(connection)
        steps.append("INIT_DB")
        for product_id, product in catalog_dict.items():
            row = {"product_id": product_id, **product}
            inserted_lines = 0
            nb_processed_lines += 1
            try:
                inserted_lines += insert_product_in_catalog(connection, row, catalog_date)
            except InvalidProductError:
                if invalid_behavior == InvalidProductBehavior.SKIP:
                    continue
                raise
            nb_inserted_lines += inserted_lines
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
        connection = connect(destination_path)
        connection.row_factory = Row
        try:
            create_logging_table(connection)
            insert_logging(connection,exec_id,source_path, catalog_date, status, error_type, ", ".join(steps),nb_processed_lines, nb_inserted_lines, start)
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