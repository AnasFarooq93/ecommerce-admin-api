from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import models
from app.schemas import schemas
from datetime import datetime

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

# ---------- POST: Create Order with Items ----------
@router.post("/", response_model=schemas.Order)
def create_order(payload: schemas.OrderCreate, db: Session = Depends(get_db)):
    total_amount = 0
    sales = []

    # Validate all products and compute total
    for item in payload.sales:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

        line_total = item.quantity * product.price
        total_amount += line_total

        sale = models.Sale(
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=product.price,
            date=datetime.utcnow()
        )
        sales.append(sale)

        # Adjust inventory
        inventory = db.query(models.Inventory).filter(models.Inventory.product_id == item.product_id).first()
        if inventory:
            inventory.quantity -= item.quantity

    # Create the order
    order = models.Order(
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        total_amount=total_amount,
        created_at=datetime.utcnow()
    )

    db.add(order)
    db.flush()  # assign order.id before inserting sales

    # Assign order_id to sales and save
    for s in sales:
        s.order_id = order.id
        db.add(s)

    db.commit()
    db.refresh(order)
    return order

# ---------- GET: All Orders ----------
@router.get("/", response_model=list[schemas.Order])
def list_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()

# ---------- GET: Order Details ----------
@router.get("/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order