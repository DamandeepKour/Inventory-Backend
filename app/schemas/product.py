from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(..., max_length=255)
    sku: str = Field(..., max_length=100)
    price: Decimal = Field(..., ge=0)
    quantity: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    sku: str | None = Field(default=None, max_length=100)
    price: Decimal | None = Field(default=None, ge=0)
    quantity: int | None = Field(default=None, ge=0)


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    sku: str
    price: Decimal
    quantity: int
    created_at: datetime
    updated_at: datetime
