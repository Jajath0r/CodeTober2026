import duckdb
from os import path


def load_daily_sales(output_dir : str, connection : duckdb.DuckDBPyConnection) -> None:
    daily_sales_path = path.join(output_dir, "daily_sales.csv")
    connection.table("daily_sales").write_csv(daily_sales_path)

def load_category_sales(output_dir : str, connection : duckdb.DuckDBPyConnection) -> None:
    category_sales_path = path.join(output_dir, "category_sales.csv")
    connection.table("category_sales").write_csv(category_sales_path)
            
def load_top_products(output_dir : str, connection : duckdb.DuckDBPyConnection) -> None:
    top_products_path = path.join(output_dir, "top_products.csv")
    connection.table("top_products").write_csv(top_products_path)
            