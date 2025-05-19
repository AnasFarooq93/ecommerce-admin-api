from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.database import get_db
from app.models import models
from app.schemas import schemas
from datetime import datetime

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

# ---------- Create Product ----------
@router.post("/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == product.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# ---------- Get Product by ID ----------
@router.get("/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# ---------- List/Filter Products ----------
@router.get("/", response_model=list[schemas.Product])
def list_products(
    name: str = Query(default=None, description="Filter by partial name"),
    sku: str = Query(default=None, description="Filter by exact SKU"),
    category_name: str = Query(default=None, description="Filter by category name"),
    min_price: float = Query(default=None, description="Minimum price"),
    max_price: float = Query(default=None, description="Maximum price"),
    in_stock: bool = Query(default=None, description="Only products in stock"),
    created_after: datetime = Query(default=None, description="Products created after this date"),
    created_before: datetime = Query(default=None, description="Products created before this date"),
    sort_by: str = Query(default="created_at", description="Sort by: name, price, created_at"),
    sort_order: str = Query(default="desc", description="Sort direction: asc or desc"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Product)

    # Join Category if filtering by category_name
    if category_name:
        query = query.join(models.Category).filter(models.Category.name.ilike(f"%{category_name}%"))

    # Filters
    if name:
        query = query.filter(models.Product.name.ilike(f"%{name}%"))
    if sku:
        query = query.filter(models.Product.sku == sku)
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
    if created_after:
        query = query.filter(models.Product.created_at >= created_after)
    if created_before:
        query = query.filter(models.Product.created_at <= created_before)

    # Filter in_stock by joining Inventory
    if in_stock is not None:
        query = query.join(models.Inventory).filter(
            models.Inventory.quantity > 0 if in_stock else models.Inventory.quantity <= 0
        )

    # Safe sorting
    allowed_sort_fields = {
        "name": models.Product.name,
        "price": models.Product.price,
        "created_at": models.Product.created_at
    }

    sort_column = allowed_sort_fields.get(sort_by, models.Product.created_at)
    if sort_order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    query = query.order_by(sort_column)

    return query.all()