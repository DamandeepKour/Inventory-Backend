from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.exceptions import ConflictError
from models.customer import Customer
from schemas.customer import CustomerCreate, CustomerUpdate


def list_customers(db: Session) -> list[Customer]:
    return db.query(Customer).order_by(Customer.created_at.desc()).all()


def get_customer(db: Session, customer_id: UUID) -> Customer:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


def create_customer(db: Session, payload: CustomerCreate) -> Customer:
    existing = db.query(Customer).filter(Customer.email == payload.email).first()
    if existing:
        raise ConflictError("Email already exists")

    customer = Customer(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def update_customer(
    db: Session, customer_id: UUID, payload: CustomerUpdate
) -> Customer:
    customer = get_customer(db, customer_id)

    if payload.email is not None and payload.email != customer.email:
        existing = db.query(Customer).filter(Customer.email == payload.email).first()
        if existing:
            raise ConflictError("Email already exists")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer


def delete_customer(db: Session, customer_id: UUID) -> None:
    customer = get_customer(db, customer_id)
    db.delete(customer)
    db.commit()
