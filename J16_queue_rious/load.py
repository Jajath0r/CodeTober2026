from sqlite3 import Connection

def create_sales_table(connection : Connection) -> None:
    connection.execute(
        "CREATE TABLE IF NOT EXISTS sales (order_id TEXT PRIMARY KEY, order_date TEXT, product_id TEXT, product_name TEXT, quantity INTEGER, unit_price_cents INTEGER, total_cents INTEGER)"
    )
    
def insert_row_in_sales(connection : Connection, row : dict[str,str]) -> None:
    connection.execute(
        "INSERT OR IGNORE INTO sales VALUES (?,?,?,?,?,?,?)",
        (row["order_id"],row["order_date"],row["product_id"],row["product_name"],row["quantity"],row["unit_price_cents"],row["total_cents"])
    )
    
def load_all_sales(connection : Connection, sales_list : list[dict[str,str]]) -> None:
    create_sales_table(connection)
    for row in sales_list:
        insert_row_in_sales(connection, row)