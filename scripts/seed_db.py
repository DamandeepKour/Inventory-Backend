#!/usr/bin/env python3
"""
Populate the database with sample products, customers, and orders.

Usage:
    cd backend
    python3 scripts/seed_db.py          # skip if data already exists
    python3 scripts/seed_db.py --force  # clear and re-seed
"""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent / "app"
sys.path.insert(0, str(APP_DIR))

from core.database import SessionLocal
from models.customer import Customer
from models.order import Order, OrderItem
from models.product import Product

PRODUCTS = [
    {"name": "Wireless Mouse", "sku": "WM-001", "price": Decimal("29.99"), "quantity": 50},
    {"name": "Mechanical Keyboard", "sku": "KB-002", "price": Decimal("89.99"), "quantity": 30},
    {"name": "USB-C Hub", "sku": "HUB-003", "price": Decimal("45.00"), "quantity": 3},
    {"name": "27\" Monitor", "sku": "MON-004", "price": Decimal("349.99"), "quantity": 12},
    {"name": "Webcam HD", "sku": "CAM-005", "price": Decimal("59.99"), "quantity": 2},
    {"name": "Laptop Stand", "sku": "LS-006", "price": Decimal("39.99"), "quantity": 25},
    {"name": "Noise Cancelling Headphones", "sku": "HP-007", "price": Decimal("199.99"), "quantity": 5},
    {"name": "External SSD 1TB", "sku": "SSD-008", "price": Decimal("129.99"), "quantity": 0},
]

CUSTOMERS = [
    {"full_name": "Alice Johnson", "email": "alice@example.com", "phone": "+1-555-0101"},
    {"full_name": "Bob Smith", "email": "bob@example.com", "phone": "+1-555-0102"},
    {"full_name": "Carol Williams", "email": "carol@example.com", "phone": "+1-555-0103"},
    {"full_name": "David Brown", "email": "david@example.com", "phone": "+1-555-0104"},
    {"full_name": "Eva Martinez", "email": "eva@example.com", "phone": "+1-555-0105"},
]


def seed(force: bool = False) -> None:
    db = SessionLocal()
    try:
        if db.query(Product).count() > 0 and not force:
            print("Database already has data. Use --force to re-seed.")
            return

        if force:
            print("Clearing existing data...")
            db.query(OrderItem).delete()
            db.query(Order).delete()
            db.query(Product).delete()
            db.query(Customer).delete()
            db.commit()

        print("Seeding products...")
        products = [Product(**p) for p in PRODUCTS]
        db.add_all(products)

        print("Seeding customers...")
        customers = [Customer(**c) for c in CUSTOMERS]
        db.add_all(customers)
        db.flush()

        print("Seeding sample orders...")
        order1 = Order(
            customer_id=customers[0].id,
            total_amount=products[0].price * 2 + products[2].price * 1,
        )
        db.add(order1)
        db.flush()

        db.add_all(
            [
                OrderItem(order_id=order1.id, product_id=products[0].id, quantity=2, price=products[0].price),
                OrderItem(order_id=order1.id, product_id=products[2].id, quantity=1, price=products[2].price),
            ]
        )
        products[0].quantity -= 2
        products[2].quantity -= 1

        order2 = Order(
            customer_id=customers[1].id,
            total_amount=products[6].price * 1,
        )
        db.add(order2)
        db.flush()
        db.add(
            OrderItem(order_id=order2.id, product_id=products[6].id, quantity=1, price=products[6].price)
        )
        products[6].quantity -= 1

        db.commit()
        print(f"Done — {len(products)} products, {len(customers)} customers, 2 orders.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed inventory database")
    parser.add_argument("--force", action="store_true", help="Clear existing data and re-seed")
    args = parser.parse_args()
    seed(force=args.force)


if __name__ == "__main__":
    main()
