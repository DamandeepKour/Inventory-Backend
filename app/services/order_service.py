from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from models.customer import Customer
from models.order import Order, OrderItem
from models.product import Product
from schemas.order import OrderCreate


def list_orders(db: Session) -> list[Order]:
    return (
        db.query(Order)
        .options(joinedload(Order.items))
        .order_by(Order.created_at.desc())
        .all()
    )


def get_order(db: Session, order_id: UUID) -> Order:
    order = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


def create_order(db: Session, payload: OrderCreate) -> Order:
    # Validate customer exists
    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    total = Decimal("0")
    line_items: list[tuple[Product, int]] = []

    # Validate products and stock before writing anything
    for item in payload.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product not found: {item.product_id}",
            )

        if product.quantity < item.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")

        total += Decimal(str(product.price)) * item.quantity
        line_items.append((product, item.quantity))

    order = Order(customer_id=payload.customer_id, total_amount=total)
    db.add(order)
    db.flush()

    for product, qty in line_items:
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=qty,
                price=product.price,
            )
        )
        product.quantity -= qty

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(order)
    return order


def delete_order(db: Session, order_id: UUID) -> None:
    order = get_order(db, order_id)

    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.quantity += item.quantity

    try:
        db.delete(order)
        db.commit()
    except Exception:
        db.rollback()
        raise
