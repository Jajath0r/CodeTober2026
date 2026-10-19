import json
from models import Product
from simulator import SimulatedCatalogSource, TransientSourceError, PermanentSourceError
from typing import Any
import time
    

def get_catalog(source: SimulatedCatalogSource) -> dict[str,Product]:
    catalog_data = fetch_catalog(source)  # objet JSON décodé : {"products": [...]}
    output_dict = {}
    for product in catalog_data["products"]:
        product_id = product["product_id"]
        output_dict[product_id] = {"name":product["name"],"unit_price_cents":product["unit_price_cents"]}
    return output_dict


def fetch_catalog(source : SimulatedCatalogSource, sleep_func = time.sleep) -> dict[str, Any]:
    attempts = 0
    delay = 0.5
    while attempts < 3:
        try:
            catalog_data = source.fetch()
        except TransientSourceError:
            attempts += 1
            if attempts == 3:
                raise
            sleep_func(delay)
            delay = min(delay + 0.5, 1)
        else:
            return catalog_data

def get_dependency_graph(graph_name : str) -> dict[str,list[str]]:
    with open(graph_name,'r') as graph:
        graph_data = json.load(graph)
    return {task["name"] : task['depends_on'] for task in graph_data['tasks']}