import duckdb

def transform_daily_sales(connection : duckdb.DuckDBPyConnection) -> None:
    connection.execute("""
        CREATE TEMP VIEW daily_sales AS
        SELECT o.order_date, COUNT(DISTINCT o.order_id) AS orders_count, SUM(i.quantity) AS items_sold, SUM(i.quantity * i.unit_price_cents) AS revenue_cents
        FROM orders o
        INNER JOIN items i
        ON o.order_id = i.order_id
        WHERE o.status = 'completed'
        GROUP BY o.order_date
        ORDER BY o.order_date ASC
    """)

def transform_category_sales(connection : duckdb.DuckDBPyConnection) -> None:
    connection.execute("""
        CREATE TEMP VIEW category_sales AS
        SELECT p.category, SUM(i.quantity) AS items_sold, SUM(i.quantity * i.unit_price_cents) AS revenue_cents
        FROM products p
        INNER JOIN items i
        ON p.product_id = i.product_id
        INNER JOIN orders o
        ON i.order_id = o.order_id
        WHERE o.status = 'completed'
        GROUP BY p.category
        ORDER BY revenue_cents DESC, p.category ASC
    """)
    
def transform_top_products(connection : duckdb.DuckDBPyConnection) -> None:
    connection.execute("""
        CREATE TEMP VIEW top_products AS
        SELECT p.product_id, p.product_name, SUM(i.quantity) AS items_sold, SUM(i.quantity * i.unit_price_cents) AS revenue_cents
        FROM products p
        INNER JOIN items i 
        ON p.product_id = i.product_id
        INNER JOIN orders o
        ON o.order_id = i.order_id
        WHERE o.status = 'completed'
        GROUP BY p.product_id, p.product_name
        ORDER BY revenue_cents DESC, p.product_id ASC
        LIMIT 5
    """)