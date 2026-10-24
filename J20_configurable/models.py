from typing import TypedDict
from enum import StrEnum

class Product(TypedDict):
    name : str
    unit_price_cents : int

class InvalidProductBehavior(StrEnum):
    FAIL = "fail"
    SKIP = "skip"
    
class InvalidProductError(ValueError):
    pass
