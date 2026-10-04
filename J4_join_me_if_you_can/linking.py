def link_order_customer(customers : dict[str,dict[str,str]], row : dict[str,str]) -> dict[str,str]:
    output_row = row.copy()
    current_customer = customers[row["customer_id"]]
    output_row["name"] = current_customer["name"]
    output_row["country"] = current_customer["country"]
    output_row["segment"] = current_customer["segment"]
    return output_row