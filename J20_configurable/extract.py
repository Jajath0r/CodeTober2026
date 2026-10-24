from models import Product, InvalidProductBehavior
import json
from typing import Any
from os import path

def get_catalog(catalog_path : str) -> dict[str, Product]:
    with open(catalog_path, "r", newline="") as catalog:
        catalog_data = json.load(catalog)
    output_dict = {}
    for product in catalog_data["products"]:
        product_id = product["product_id"]
        output_dict[product_id] = {"name":product["name"],"unit_price_cents":product["unit_price_cents"]}
    return output_dict

def validate_config_file(input_json : Any) -> None:
    expected_keys = {"source", "destination", "behavior"}
    if not isinstance(input_json, dict) or set(input_json.keys()) != expected_keys:
        raise ValueError("Invalid configuration structure")
    if not isinstance(input_json["source"], dict) or set(input_json["source"].keys()) != {"path"}:
        raise ValueError("Invalid source configuration")
    if not isinstance(input_json["destination"], dict) or set(input_json["destination"].keys()) != {"sqlite_path"}:
        raise ValueError("Invalid destination configuration")
    if not isinstance(input_json["behavior"],dict) or set(input_json["behavior"].keys()) != {"invalid_product"}:
        raise ValueError("Invalid behavior configuration")
        

def get_configuration_data(input_json : str) -> dict[str, dict[str, str]]:
    with open(input_json,"r",newline="") as config:
        json_data = json.load(config)
    validate_config_file(json_data)
    return json_data
    

def get_source_file(config_dir : str, config: dict[str, dict[str, str]]) -> str:
    try:
        source = config["source"]["path"]
    except KeyError as e:
        raise ValueError("Missing source in config") from e
    if not isinstance(source, str) or not source.strip():
        raise ValueError("Source must be a non-empty string")
    return path.abspath(path.join(config_dir,source))
    
def get_destination_file(config_dir : str,config : dict[str, dict[str, str]]) -> str:
    try:
        dest = config["destination"]["sqlite_path"]
    except KeyError as e:
        raise ValueError("Missing destination in config") from e
    if not isinstance(dest, str) or not dest.strip():
            raise ValueError("Destination must be a non-empty string")
    return path.abspath(path.join(config_dir,dest))

def get_invalid_product_behavior(config : dict[str, dict[str, str]]) -> InvalidProductBehavior:
    try:
        invalid_behavior = config["behavior"]["invalid_product"]
    except KeyError as e:
        raise ValueError("Missing invalid behavior in config") from e

    return InvalidProductBehavior(invalid_behavior)

