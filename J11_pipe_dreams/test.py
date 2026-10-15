import pytest
from main import create_sales_row, create_sales_table, insert_row_in_sales
from sqlite3 import connect


@pytest.mark.parametrize(
    "quantity, catalog_price, order_price, expected_total",
    [
        ("2", 850, None, 1700),
        ("1", 850, None, 850),
        ("3", 0, None, 0),
        ("100", 850, None, 85000),
        ("3", 850, "9999", 2550),  # Test 2 : prix contradictoire
    ]
)
def test_create_sales_row(
    quantity, catalog_price, order_price, expected_total
):
    order = {
        "order_id": "ORD-001",
        "order_date": "2026-10-12",
        "product_id": "P-101",
        "quantity": quantity,
        "status": "paid"
    }

    if order_price is not None:
        order["unit_price_cents"] = order_price

    catalog = {
        "P-101": {
            "name": "Notebook",
            "unit_price_cents": catalog_price
        }
    }

    result = create_sales_row("P-101", order, catalog)

    assert result["unit_price_cents"] == catalog_price
    assert result["total_cents"] == expected_total
    
    

def test_insert_row_in_sales():
    connection = connect(":memory:")
    create_sales_table(connection)

    sale = {
        "order_id": "ORD-001",
        "order_date": "2026-10-12",
        "product_id": "P-101",
        "product_name": "Notebook",
        "quantity": 2,
        "unit_price_cents": 850,
        "total_cents": 1700
    }

    expected = (
        "ORD-001", "2026-10-12", "P-101",
        "Notebook", 2, 850, 1700
    )

    insert_row_in_sales(connection, sale)

    assert connection.execute(
        "SELECT COUNT(*) FROM sales"
    ).fetchone()[0] == 1

    assert connection.execute(
        "SELECT * FROM sales"
    ).fetchone() == expected

    # Deuxième insertion : même commande
    modified_sale = sale.copy()
    modified_sale["total_cents"] = 9999

    insert_row_in_sales(connection, modified_sale)

    assert connection.execute(
        "SELECT COUNT(*) FROM sales"
    ).fetchone()[0] == 1

    assert connection.execute(
        "SELECT * FROM sales"
    ).fetchone() == expected

    connection.close()