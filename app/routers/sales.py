from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from datetime import datetime, timedelta
from app.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(
    prefix="/sales",
    tags=["Sales"]
)

# ---------- Record Sale ----------
@router.post("/", response_model=schemas.Sale)
def record_sale(payload: schemas.SaleCreate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    unit_price = product.price
    sale = models.Sale(
        product_id=payload.product_id,
        quantity=payload.quantity,
        unit_price=unit_price,
        date=payload.date or datetime.utcnow(),
        order_id=payload.order_id
    )

    inventory = db.query(models.Inventory).filter(models.Inventory.product_id == payload.product_id).first()
    if inventory:
        inventory.quantity -= payload.quantity

    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale

# ---------- Get Sales (with filters) ----------
@router.get("/", response_model=list[schemas.Sale])
def get_sales(
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    product_name: str = Query(default=None),
    category_name: str = Query(default=None),
    db: Session = Depends(get_db)
):
    query = db.query(models.Sale).join(models.Product)

    if product_name:
        query = query.filter(models.Product.name.ilike(f"%{product_name}%"))
    if category_name:
        query = query.join(models.Category).filter(models.Category.name.ilike(f"%{category_name}%"))
    if start_date:
        query = query.filter(models.Sale.date >= start_date)
    if end_date:
        query = query.filter(models.Sale.date <= end_date)

    return query.all()

# ---------- Revenue Summary ----------
@router.get("/revenue-summary")
def revenue_summary(
    range_type: str = Query(default="daily", description="daily, weekly, monthly, yearly"),
    db: Session = Depends(get_db)
):
    # Determine time field
    if range_type == "daily":
        label = func.date(models.Sale.date)
    elif range_type == "weekly":
        label = func.concat(
            func.year(models.Sale.date), "-W", func.week(models.Sale.date)
        )
    elif range_type == "monthly":
        label = func.concat(
            func.year(models.Sale.date), "-", func.month(models.Sale.date)
        )
    elif range_type == "yearly":
        label = func.year(models.Sale.date)
    else:
        raise HTTPException(status_code=400, detail="Invalid range_type")

    results = db.query(
        label.label("period"),
        func.sum(models.Sale.quantity * models.Sale.unit_price).label("revenue")
    ).group_by(label).order_by(label).all()

    return results

# ---------- Compare Revenue ----------
@router.get("/compare")
def compare_revenue(
    group_by: str = Query(default="category", description="category or product"),
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: Session = Depends(get_db)
):
    query = db.query(
        func.sum(models.Sale.quantity * models.Sale.unit_price).label("revenue")
    )

    if group_by == "category":
        query = query.add_columns(models.Category.name.label("category")) \
            .join(models.Product).join(models.Category) \
            .filter(models.Sale.date.between(start_date, end_date)) \
            .group_by(models.Category.name)
    elif group_by == "product":
        query = query.add_columns(models.Product.name.label("product")) \
            .join(models.Product) \
            .filter(models.Sale.date.between(start_date, end_date)) \
            .group_by(models.Product.name)
    else:
        raise HTTPException(status_code=400, detail="Invalid group_by")

    return query.all()