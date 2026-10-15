import json
from models import Product
    
def get_catalog(json_file : str) -> dict[str,Product]:
    with open(json_file) as catalog:
        catalog_dict = json.load(catalog)
    output_dict = {}
    for product in catalog_dict["products"]:
        product_id = product["product_id"]
        output_dict[product_id] = {"name":product["name"],"unit_price_cents":product["unit_price_cents"]}
    return output_dict
