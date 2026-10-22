from models import Product
import json

def get_catalog(catalog_path : str) -> dict[str, Product]:
    with open(catalog_path, "r", newline="") as catalog:
        catalog_data = json.load(catalog)
    output_dict = {}
    for product in catalog_data["products"]:
        product_id = product["product_id"]
        output_dict[product_id] = {"name":product["name"],"unit_price_cents":product["unit_price_cents"]}
    return output_dict

