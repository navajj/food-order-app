from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class RestaurantOut(BaseModel):
    id: int
    name: str
    description: str
    is_active: bool

    class Config:
        from_attributes = True


class MenuItemOut(BaseModel):
    id: int
    restaurant_id: int
    name: str
    description: str
    price: Decimal
    is_available: bool
    category: str

    class Config:
        from_attributes = True


class MenuItemCreate(BaseModel):
    name: str
    description: str = ""
    price: Decimal
    category: str = ""
    is_available: bool = True


class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = 1


class OrderItemOut(BaseModel):
    id: int
    menu_item_id: int
    menu_item_name: str
    quantity: int
    unit_price: Decimal

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    restaurant_id: int
    items: list[OrderItemCreate]
    notes: str = ""


class OrderOut(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int
    restaurant_name: str
    status: str
    total: Decimal
    notes: str
    items: list[OrderItemOut]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str


class CustomerOut(BaseModel):
    id: int
    user_id: int
    phone: str
    address: str

    class Config:
        from_attributes = True


class CustomerUpdate(BaseModel):
    phone: Optional[str] = None
    address: Optional[str] = None
