import duckdb
from os import path

def load_parquet(connection : duckdb.DuckDBPyConnection, output_dir : str) -> None:
    lake_dir = path.join(output_dir,"lake")
    query = f"""COPY temp_sales
    TO '{lake_dir}'
    (
        FORMAT PARQUET,
        COMPRESSION ZSTD,
        PARTITION BY (order_month, country),
        OVERWRITE TRUE
    );"""
    
    connection.execute(query)
    
def load_monthly_summary(connection : duckdb.DuckDBPyConnection, output_dir : str) -> None:
    monthly_summary_path = path.join(output_dir,"monthly_summary.csv")
    connection.table("monthly_summary").write_csv(monthly_summary_path)
    
def load_selected_sales(connection : duckdb.DuckDBPyConnection, output_dir : str) -> None:
    selected_sales_path = path.join(output_dir, "selected_sales.csv")
    connection.table("selected_sales").write_csv(selected_sales_path)
    