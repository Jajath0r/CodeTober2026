import duckdb
from os import path
from pathlib import Path

def transform_sales_data(connection : duckdb.DuckDBPyConnection) -> None:
    query = f"""
        CREATE TEMP VIEW temp_sales AS
        SELECT
            CAST(transaction_id AS VARCHAR) AS transaction_id,
            CAST(order_date AS DATE) AS order_date,
            CAST(country AS VARCHAR) AS country,
            CAST(product_id AS VARCHAR) AS product_id,
            CAST(status AS VARCHAR) AS status,
            CAST(quantity AS INTEGER) AS quantity,
            CAST(unit_price_cents AS INTEGER) AS unit_price_cents,
            STRFTIME(CAST(order_date AS DATE), '%Y-%m') AS order_month
        FROM sales;
    """
    
    connection.execute(query)


def transform_monthly_summary(connection : duckdb.DuckDBPyConnection) -> None:
    query = f"""
        CREATE TEMP VIEW monthly_summary AS
        SELECT 
            order_month,
            country,
            COUNT(*) AS transactions_count,
            SUM(quantity) AS items_sold,
            SUM(quantity * unit_price_cents) AS revenue_cents
        FROM temp_sales
        WHERE status = 'completed'
        GROUP BY order_month, country
        ORDER BY order_month, country
    """
    connection.execute(query)

def transform_selected_sales(connection : duckdb.DuckDBPyConnection, output_dir : str, order_month : str, country : str) -> None:    
    parquet_path = Path(output_dir) / "lake" / f"order_month={order_month}" / f"country={country}"

    parquet_files = list(parquet_path.glob("*.parquet"))

    if parquet_files:
        query = f"""
            CREATE TEMP VIEW selected_sales AS
            SELECT
                transaction_id,
                order_date,
                country,
                product_id,
                status,
                quantity,
                unit_price_cents
            FROM read_parquet('{parquet_path}/*.parquet')
            ORDER BY transaction_id ASC
        """
    else:
        query = """
            CREATE TEMP VIEW selected_sales AS
            SELECT
                CAST(NULL AS VARCHAR) AS transaction_id,
                CAST(NULL AS DATE) AS order_date,
                CAST(NULL AS VARCHAR) AS country,
                CAST(NULL AS VARCHAR) AS product_id,
                CAST(NULL AS VARCHAR) AS status,
                CAST(NULL AS INTEGER) AS quantity,
                CAST(NULL AS INTEGER) AS unit_price_cents
            WHERE FALSE;
        """
        
    connection.execute(query)