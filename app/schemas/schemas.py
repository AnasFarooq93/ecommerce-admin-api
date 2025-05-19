from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# ---------- Category ----------

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    model_config = {
        "from_attributes": True
    }

# ---------- Product ----------

class ProductBase(BaseModel):
    name: str
    category_id: int
    price: float
    description: Optional[str] = None
    sku: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[Category] = None

    model_config = {
        "from_attributes": True
    }

# ---------- Inventory ----------

class InventoryBase(BaseModel):
    product_id: int
    quantity: int

class InventoryCreate(InventoryBase):
    pass

class Inventory(InventoryBase):
    id: int
    last_updated: datetime
    product: Optional[Product] = None

    model_config = {
        "from_attributes": True
    }

# ---------- Sale ----------

class SaleBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

class SaleCreate(SaleBase):
    order_id: Optional[int] = None
    date: Optional[datetime] = None

class Sale(SaleBase):
    id: int
    date: datetime
    order_id: Optional[int]
    product: Optional[Product] = None

    model_config = {
        "from_attributes": True
    }

# ---------- Order ----------

class OrderBase(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    total_amount: float

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    created_at: datetime
    sales: List[Sale] = []

    model_config = {
        "from_attributes": True
    }