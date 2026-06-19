from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.exceptions import ConflictError
from models.product import Product
from schemas.product import ProductCreate, ProductUpdate


def list_products(db: Session) -> list[Product]:
    return db.query(Product).order_by(Product.created_at.desc()).all()


def get_product(db: Session, product_id: UUID) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def create_product(db: Session, payload: ProductCreate) -> Product:
    if payload.quantity < 0:
        raise HTTPException(status_code=400, detail="Quantity cannot be negative")

    existing = db.query(Product).filter(Product.sku == payload.sku).first()
    if existing:
        raise ConflictError("SKU already exists")

    product = Product(
        name=payload.name,
        sku=payload.sku,
        price=payload.price,
        quantity=payload.quantity,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: UUID, payload: ProductUpdate) -> Product:
    product = get_product(db, product_id)

    if payload.quantity is not None and payload.quantity < 0:
        raise HTTPException(status_code=400, detail="Quantity cannot be negative")

    if payload.sku is not None and payload.sku != product.sku:
        existing = db.query(Product).filter(Product.sku == payload.sku).first()
        if existing:
            raise ConflictError("SKU already exists")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: UUID) -> None:
    product = get_product(db, product_id)
    db.delete(product)
    db.commit()
