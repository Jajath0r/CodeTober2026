import pytest
from extract import extract_products,extract_order_items,extract_orders
from transform import transform_daily_sales,transform_category_sales,transform_top_products
from load import load_category_sales,load_daily_sales,load_top_products
import duckdb
import csv

def write_csv(file_path, rows):
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(rows[0].keys())
        )
        writer.writeheader()
        writer.writerows(rows)
        
def test_multiple_items_same_order(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    orders = [
        {
            "order_id": "O001",
            "order_date": "2026-10-01",
            "country": "FR",
            "status": "completed"
        },
        {
            "order_id": "O002",
            "order_date": "2026-10-01",
            "country": "FR",
            "status": "completed"
        }
    ]
    write_csv(data_dir / "orders.csv", orders)
    order_items = [
        {
            "item_id" : "I001",
            "order_id" : "O001",
            "product_id" : "P001",
            "quantity" : 2,
            "unit_price_cents" : 1000
        },
        {
            "item_id" : "I002",
            "order_id" : "O001",
            "product_id" : "P002",
            "quantity" : 3,
            "unit_price_cents" : 500
        },
        {
            "item_id" : "I003",
            "order_id" : "O002",
            "product_id" : "P001",
            "quantity" : 1,
            "unit_price_cents" : 1000
        }
                     
    ]
    write_csv(data_dir / "order_items.csv", order_items)
    products = [
        {
            "product_id":"P001",
            "product_name":"Clavier compact",
            "category":"Peripheriques",
            "unit_price_cents":3900
        },
        {
            "product_id":"P002",
            "product_name":"Souris sans fil",
            "category":"Peripheriques",
            "unit_price_cents":2400
        }
    ]
    write_csv(data_dir / "products.csv", products)
    
    with duckdb.connect(":memory:") as connection:
        extract_orders(connection,str(data_dir))
        extract_order_items(connection,str(data_dir))
        extract_products(connection,str(data_dir))
        
        transform_daily_sales(connection)
        
        result = connection.execute("""
            SELECT orders_count, items_sold, revenue_cents
            FROM daily_sales
            WHERE order_date = '2026-10-01'
        """).fetchone()
        
    assert result == (2, 6, 4500)
    
def test_invalid_status(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    orders = [
        {
            "order_id": "O001",
            "order_date": "2026-10-01",
            "country": "FR",
            "status": "cancelled"
        },
        {
            "order_id": "O002",
            "order_date": "2026-10-01",
            "country": "FR",
            "status": "pending"
        }
    ]
    write_csv(data_dir / "orders.csv", orders)
    order_items = [
        {
            "item_id" : "I001",
            "order_id" : "O001",
            "product_id" : "P001",
            "quantity" : 2,
            "unit_price_cents" : 1000
        },
        {
            "item_id" : "I002",
            "order_id" : "O001",
            "product_id" : "P002",
            "quantity" : 3,
            "unit_price_cents" : 500
        },
        {
            "item_id" : "I003",
            "order_id" : "O002",
            "product_id" : "P001",
            "quantity" : 1,
            "unit_price_cents" : 1000
        }
                     
    ]
    write_csv(data_dir / "order_items.csv", order_items)
    products = [
        {
            "product_id":"P001",
            "product_name":"Clavier compact",
            "category":"Peripheriques",
            "unit_price_cents":3900
        },
        {
            "product_id":"P002",
            "product_name":"Souris sans fil",
            "category":"Peripheriques",
            "unit_price_cents":2400
        }
    ]
    write_csv(data_dir / "products.csv", products)
    
    with duckdb.connect(":memory:") as connection:
        extract_orders(connection,str(data_dir))
        extract_order_items(connection,str(data_dir))
        extract_products(connection,str(data_dir))
        
        transform_daily_sales(connection)
        transform_top_products(connection)
        transform_category_sales(connection)
        for view in ("daily_sales", "category_sales", "top_products"):
            result = connection.execute(
                f"SELECT COUNT(*) FROM {view}"
            ).fetchone()

            assert result[0] == 0
            
            
def test_no_regression(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    orders = [
        {
            "order_id": "O001",
            "order_date": "2026-10-01",
            "country": "FR",
            "status": "cancelled"
        },
        {
            "order_id": "O002",
            "order_date": "2026-10-01",
            "country": "FR",
            "status": "pending"
        },
        {
            "order_id": "O003",
            "order_date": "2026-10-01",
            "country": "FR",
            "status": "completed"
        }
    ]
    write_csv(data_dir / "orders.csv", orders)
    order_items = [
        {
            "item_id" : "I001",
            "order_id" : "O001",
            "product_id" : "P001",
            "quantity" : 100,
            "unit_price_cents" : 100000
        },
        {
            "item_id" : "I002",
            "order_id" : "O002",
            "product_id" : "P002",
            "quantity" : 200,
            "unit_price_cents" : 100000
        },
        {
            "item_id" : "I003",
            "order_id" : "O003",
            "product_id" : "P001",
            "quantity" : 2,
            "unit_price_cents" : 1000
        }
                     
    ]
    write_csv(data_dir / "order_items.csv", order_items)
    products = [
        {
            "product_id":"P001",
            "product_name":"Clavier compact",
            "category":"Peripheriques",
            "unit_price_cents":3900
        },
        {
            "product_id":"P002",
            "product_name":"Souris sans fil",
            "category":"Peripheriques",
            "unit_price_cents":2400
        }
    ]
    write_csv(data_dir / "products.csv", products)
    
    with duckdb.connect(":memory:") as connection:
        extract_orders(connection,str(data_dir))
        extract_order_items(connection,str(data_dir))
        extract_products(connection,str(data_dir))
        
        transform_daily_sales(connection)
        transform_top_products(connection)
        transform_category_sales(connection)
        
        daily_sales_result = connection.execute("""
            SELECT orders_count, items_sold, revenue_cents
            FROM daily_sales
            WHERE order_date = '2026-10-01'
        """).fetchone()
        category_sales_result = connection.execute("""
            SELECT category, items_sold, revenue_cents
            FROM category_sales
        """).fetchall()

        top_products_result = connection.execute("""
            SELECT product_id, items_sold, revenue_cents
            FROM top_products
        """).fetchall()
        
    assert daily_sales_result == (1, 2, 2000)
    assert category_sales_result == [("Peripheriques",2,2000)]
    assert top_products_result == [("P001",2,2000)]

def test_ex_aequo(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    orders = [
        {
            "order_id": "O001",
            "order_date": "2026-10-01",
            "country": "FR",
            "status": "completed"
        },
        {
            "order_id": "O002",
            "order_date": "2026-10-01",
            "country": "FR",
            "status": "completed"
        },
        {
            "order_id": "O003",
            "order_date": "2026-10-01",
            "country": "FR",
            "status": "completed"
        }
    ]
    order_items = [
        {
            "item_id": "I001",
            "order_id": "O001",
            "product_id": "P002",
            "quantity": 2,
            "unit_price_cents": 2500
        },
        {
            "item_id": "I002",
            "order_id": "O002",
            "product_id": "P003",
            "quantity": 3,
            "unit_price_cents": 1000
        },
        {
            "item_id": "I003",
            "order_id": "O003",
            "product_id": "P001",
            "quantity": 5,
            "unit_price_cents": 1000
        }
    ]
    products = [
        {
            "product_id": "P002",
            "product_name": "Souris",
            "category": "Peripheriques",
            "unit_price_cents": 2500
        },
        {
            "product_id": "P003",
            "product_name": "Webcam",
            "category": "Peripheriques",
            "unit_price_cents": 1000
        },
        {
            "product_id": "P001",
            "product_name": "Clavier",
            "category": "Peripheriques",
            "unit_price_cents": 1000
        }
    ]

    write_csv(data_dir / "orders.csv", orders)
    write_csv(data_dir / "order_items.csv", order_items)
    write_csv(data_dir / "products.csv", products)
    
    with duckdb.connect(":memory:") as connection:
        extract_orders(connection,str(data_dir))
        extract_order_items(connection,str(data_dir))
        extract_products(connection,str(data_dir))
        
        transform_top_products(connection)
        
        result = connection.execute("""
            SELECT product_id, items_sold, revenue_cents
            FROM top_products
        """).fetchall()
        
    assert result == [
        ("P001", 5, 5000),
        ("P002", 2, 5000),
        ("P003", 3, 3000)
    ]
    
    write_csv(
        data_dir / "order_items.csv",
        list(reversed(order_items))
    )

    with duckdb.connect(":memory:") as connection:
        extract_orders(connection, str(data_dir))
        extract_order_items(connection, str(data_dir))
        extract_products(connection, str(data_dir))

        transform_top_products(connection)

        reversed_result = connection.execute("""
            SELECT product_id, items_sold, revenue_cents
            FROM top_products
        """).fetchall()

    assert reversed_result == result
       
