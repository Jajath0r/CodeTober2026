from sqlite3 import Connection
from datetime import date
from time import perf_counter

def create_catalog_table(connection : Connection) -> None:
    connection.execute(
        "CREATE TABLE IF NOT EXISTS catalog (product_id TEXT, name TEXT, unit_price_cents INT, valid_from TEXT, valid_to TEXT, PRIMARY KEY (product_id, valid_from))"
    )
    
def create_logging_table(connection : Connection) -> None:
    connection.execute(
        "CREATE TABLE IF NOT EXISTS logging (exec_id TEXT PRIMARY KEY, source TEXT, effect_date TEXT, status TEXT, error_type TEXT, finished_steps TEXT, nb_processed_lines INTEGER, nb_inserted_lines INTEGER, duration_ms REAL)"
    )

def insert_logging(
    connection : Connection,
    exec_id : str,
    source : str,
    effect_date : str,
    status : str,
    error_type : str | None,
    finished_steps : str,
    nb_processed_lines : int,
    nb_inserted_lines : int,
    start : float) -> None :
    connection.execute(
        "INSERT INTO logging (exec_id, source, effect_date, status, error_type, finished_steps,nb_processed_lines, nb_inserted_lines, duration_ms) VALUES (?,?,?,?,?,?,?,?,?)",
        (exec_id,source, effect_date, status, error_type,finished_steps, nb_processed_lines,nb_inserted_lines, (perf_counter() - start) * 1000)
    )

def insert_product_in_catalog(connection : Connection, row : dict[str,str], current_date : str) -> int:
    product_id = row["product_id"]
    name = row["name"]
    price = int(row["unit_price_cents"])
    snapshot_date = date.fromisoformat(current_date)
    latest_product = connection.execute(
        "SELECT * FROM catalog where product_id = ? and valid_to is NULL",
        (row["product_id"],)
    ).fetchone()
    if latest_product is not None:
        prev_date = date.fromisoformat(latest_product["valid_from"])
        if snapshot_date < prev_date:
            raise ValueError(f"Out-of-order catalog for {product_id}")       
        unchanged = (latest_product["name"] == name and latest_product["unit_price_cents"] == price)
        if unchanged:
            return 0
        if snapshot_date == prev_date:
            raise ValueError(f"Conflicting versions on {current_date} for {product_id}")
        connection.execute(
            "UPDATE catalog SET valid_to = ? WHERE product_id = ? AND valid_to IS NULL",
            (current_date, product_id)
        )
    connection.execute(
        "INSERT INTO catalog (product_id, name, unit_price_cents, valid_from, valid_to) VALUES (?,?,?,?,?)",
        (product_id,name,price,current_date,None)
    )
    return  1