import argparse
from sqlite3 import connect,Row
from os import path,makedirs
import csv
from extract import get_catalog, get_dependency_graph
from transform import validate_input_schema,create_sales_row
from load import create_sales_table, insert_row_in_sales
from simulator import SimulatedCatalogSource
from orchestrator import execute_function_in_order,validate_graph


    
def parse_input():
    parser = argparse.ArgumentParser(
        description="Retry me maybe"
    )
    
    parser.add_argument(
        "input_rep",
        type=str,
        help="path of input files"
    )
    parser.add_argument(
        "input_file_name",
        type=str,
        help="name of orders file"
    )
    parser.add_argument(
        "scenario",
        type=str,
        help="wanted scenario"
    )
    parser.add_argument(
        "dependancy_graph",
        type=str,
        help="dependancy graph to take as input"
    )
    
    return parser.parse_args()


def main():
    args = parse_input()
    # input_rep = args.input_rep
    output_rep ="output"
    # scenario = args.scenario
    graph_name = args.dependancy_graph
    if not path.exists(output_rep):
        makedirs(output_rep)
    # db_path = path.join(output_rep,"sales.db")
    # connection = connect(db_path)
    # connection.row_factory = Row
    # orders_file = path.join(input_rep,args.input_file_name)
    # source = SimulatedCatalogSource(path.join(input_rep, "catalog.json"),scenario=scenario)
    graph_dict = get_dependency_graph(graph_name)
    validate_graph(graph_dict)
    tasks_status = execute_function_in_order(graph_dict)
    
    # try:
    #     create_sales_table(connection)
    #     catalog = get_catalog(source)
    #     with open(orders_file, "r", newline="") as orders:
    #         r = csv.DictReader(orders)
    #         quantity_key = validate_input_schema(set(r.fieldnames or []))

    #         for row in r:
    #             if row["status"] == "paid":
    #                 product_id = row["product_id"]

    #                 if product_id in catalog:
    #                     sales_row = create_sales_row(
    #                         product_id, row, catalog, quantity_key
    #                     )
    #                     insert_row_in_sales(connection, sales_row)
    # except Exception:
    #     connection.rollback()
    #     raise
    # else:
    #     connection.commit()
    # finally:
    #     connection.close()
if __name__ == "__main__":
    main()