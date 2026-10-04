from datetime import datetime
import json

def is_valid_event_id(row : dict[str,str]) -> bool:
    return row["event_id"] !=""

def is_valid_event_type(row : dict[str,str]) -> bool:
    event_types = ["order_created","payment_received","customer_updated"]
    return row["event_type"] in event_types

def is_valid_event_version(row : dict[str,str]) -> bool:
    event_versions = ['1','2']
    return row["event_version"] in event_versions

def is_valid_timestamp(row : dict[str,str]) -> bool:
    try:
        datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S")
        return True
    except ValueError:
        return False

def is_valid_customer_id(row : dict[str,str]) -> bool:
    return row["customer_id"] != ''

def is_valid_metadata(row : dict[str,str]) -> bool:
    metadata = row["metadata"]
    try:
        json.loads(metadata)
    except ValueError as e:
        return False
    return metadata != ""

def has_correct_amount(row : dict[str,str]) -> bool:
    if row["amount"] =="":return True
    try:
        amount = float(row['amount'])
        return (amount > 0)
    except ValueError:
        return False

def has_correct_currency(row : dict[str,str]) -> bool:
    currencies = ["EUR","USD","GBP", ""]
    return row["currency"] in currencies

def has_correct_country(row : dict[str,str]) -> bool:
    country = row["country"]
    return country == "" or (country.isalpha() and len(country) == 2)

def is_empty_field(fieldname : str, row : dict[str,str]) -> bool:
    return row[fieldname] == ""

def get_error_list(row : dict[str,str]) -> list[str]:
    error_list=[]
    if not is_valid_event_id(row):error_list.append("NO_EVENT_ID")
    if not is_valid_event_type(row):error_list.append("WRONG_EVENT_TYPE")
    if not is_valid_event_version(row):error_list.append("WRONG_EVENT_VERSION")
    if not is_valid_timestamp(row):error_list.append("WRONG_TIMESTAMP")
    if not is_valid_customer_id(row):error_list.append("NO_CUSTOMER_ID")
    if not has_correct_currency(row):error_list.append("INCORRECT_CURRENCY")
    if not has_correct_amount(row):error_list.append("INCORRECT_AMOUNT")
    if not has_correct_country(row):error_list.append("INCORRECT_COUNTRY")
    if not is_valid_metadata(row):error_list.append("INCORRECT_JSON_IN_METADATA")
    if is_valid_event_type(row):
        if row["event_type"] in ["order_created","payment_received"]:
            if is_empty_field('currency',row):error_list.append("NO_CURRENCY_FOR_ORDER_OR_PAYMENT")
            if is_empty_field('amount',row):error_list.append("NO_AMOUNT_FOR_ORDER_OR_PAYMENT")
            if is_empty_field('country',row):error_list.append("NO_COUNTRY_FOR_ORDER_OR_PAYMENT")
    return error_list

def increment_event_type_dict(row : dict[str,str], event_type_dict : dict[str,int]) -> dict[str,int]:
    if is_valid_event_type(row):
        event_type_dict[row["event_type"]] += 1
    return event_type_dict