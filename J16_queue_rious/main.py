import argparse
from sqlite3 import connect,Row
from os import path,makedirs
import csv
from extract import get_catalog,produce_orders
from transform import consume_orders
from load import load_all_sales
from simulator import SimulatedCatalogSource
from queue import Queue
from concurrent.futures import ThreadPoolExecutor


    
def parse_input():
    parser = argparse.ArgumentParser(
        description="Queue-rious"
    )
    
    parser.add_argument(
        "input_rep",
        type=str,
        help="path of input files"
    )
    parser.add_argument(
        "input_files",
        nargs="+",
        type=str,
        help="csv files to process"
    )
    parser.add_argument(
        "max_queue_size",
        type=int,
        help='maximum queue size'
    )
    return parser.parse_args()


def main():
    args = parse_input()
    input_rep = args.input_rep
    output_rep ="output"
    max_queue_size = args.max_queue_size
    # On fixe le scenario à "healthy", ce n'est pas le sujet de jour, on ne s'encombre pas avec ça
    scenario = "healthy"
    if not path.exists(output_rep):
        makedirs(output_rep)
    db_path = path.join(output_rep,"sales.db")
    connection = connect(db_path)
    connection.row_factory = Row
    orders_files = []
    for file in args.input_files:
        orders_files.append(path.join(input_rep,file))
    source = SimulatedCatalogSource(path.join(input_rep, "catalog.json"),scenario=scenario)    
    try:
        catalog = get_catalog(source)
        sales_queue = Queue(maxsize=max_queue_size)
        producer_futures = []
        producer_errors = []
        consumer_futures = []
        sales_rows = []
        errors_list = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            for order_file in orders_files:
                future = executor.submit(produce_orders,order_file,sales_queue)
                producer_futures.append(future)
            for _ in range(2):
                future = executor.submit(consume_orders,sales_queue,catalog)
                consumer_futures.append(future)
            try:
                for producer in producer_futures:
                    try:
                        producer.result()
                    except Exception as e:
                        producer_errors.append(e)
            finally:
                for _ in consumer_futures:
                    sales_queue.put(None)
            
            for consumer in consumer_futures:
                consumer_sales, consumer_errors = consumer.result()
                sales_rows.extend(consumer_sales)
                errors_list.extend(consumer_errors)
            if producer_errors:
                raise producer_errors[0]
        load_all_sales(connection,sales_rows)
    except Exception:
        connection.rollback()
        raise
    else:
        connection.commit()
    finally:
        connection.close()
if __name__ == "__main__":
    main()