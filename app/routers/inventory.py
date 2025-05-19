from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)

# ---------- GET: View & Filter Inventory ----------
@router.get("/", response_model=list[schemas.Inventory])
def get_inventory(
    product_name: str = Query(default=None),
    category_name: str = Query(default=None),
    sku: str = Query(default=None),
    min_qty: int = Query(default=None),
    max_qty: int = Query(default=None),
    sort_by: str = Query(default="last_updated"),
    sort_order: str = Query(default="desc"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Inventory).join(models.Product)

    if product_name:
        query = query.filter(models.Product.name.ilike(f"%{product_name}%"))
    if category_name:
        query = query.join(models.Category).filter(models.Category.name.ilike(f"%{category_name}%"))
    if sku:
        query = query.filter(models.Product.sku == sku)
    if min_qty is not None:
        query = query.filter(models.Inventory.quantity >= min_qty)
    if max_qty is not None:
        query = query.filter(models.Inventory.quantity <= max_qty)

    allowed_sort_fields = {
        "quantity": models.Inventory.quantity,
        "last_updated": models.Inventory.last_updated,
        "product_name": models.Product.name
    }

    sort_column = allowed_sort_fields.get(sort_by, models.Inventory.last_updated)
    query = query.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc())

    return query.all()

# ---------- GET: Low Stock Alert ----------
@router.get("/low-stock", response_model=list[schemas.Inventory])
def low_stock(threshold: int = 5, db: Session = Depends(get_db)):
    return db.query(models.Inventory).filter(models.Inventory.quantity <= threshold).all()

# ---------- POST: Add or Update Inventory ----------
@router.post("/", response_model=schemas.Inventory)
def upsert_inventory(payload: schemas.InventoryCreate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    inventory = db.query(models.Inventory).filter(models.Inventory.product_id == payload.product_id).first()
    if inventory:
        inventory.quantity = payload.quantity
    else:
        inventory = models.Inventory(**payload.model_dump())
        db.add(inventory)

    db.commit()
    db.refresh(inventory)
    return inventory