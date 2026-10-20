from typing import TypedDict

class Product(TypedDict):
    sku : str
    name : str
    price_cents : int

class ProviderResult(TypedDict):
    catalog : list[Product] | None
    errors : str | None