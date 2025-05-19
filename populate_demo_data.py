from app.database import SessionLocal, engine
from app.models import models
import datetime

# Create tables
models.Base.metadata.create_all(bind=engine)

# Initialize DB session
db = SessionLocal()

# ---------- Categories ----------
categories = {
    "Electronics": models.Category(name="Electronics"),
    "Fashion": models.Category(name="Fashion"),
    "Health": models.Category(name="Health"),
}
db.add_all(categories.values())
db.commit()

# ---------- Products ----------
products = [
    models.Product(
        name="Smart Watch Series 5",
        category_id=categories["Electronics"].id,
        price=199.99,
        description="Fitness tracking, heart rate monitor, GPS",
        sku="ELEC-001",
    ),
    models.Product(
        name="Bluetooth Earbuds X1",
        category_id=categories["Electronics"].id,
        price=89.99,
        description="Noise cancelling, 20-hour battery life",
        sku="ELEC-002",
    ),
    models.Product(
        name="Men's Running Sneakers",
        category_id=categories["Fashion"].id,
        price=129.50,
        description="Comfortable athletic shoes with shock absorption",
        sku="FASH-001",
    ),
]
db.add_all(products)
db.commit()

# ---------- Inventory ----------
inventory = [
    models.Inventory(product_id=1, quantity=150),
    models.Inventory(product_id=2, quantity=80),
    models.Inventory(product_id=3, quantity=200),
]
db.add_all(inventory)
db.commit()

# ---------- Orders + Sales ----------
orders = [
    {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [
            {"product_id": 1, "quantity": 1},
            {"product_id": 2, "quantity": 2}
        ]
    },
    {
        "customer_name": "Sara Smith",
        "customer_email": "sara@example.com",
        "items": [
            {"product_id": 3, "quantity": 3}
        ]
    }
]

for order_data in orders:
    total = 0
    sales = []
    for item in order_data["items"]:
        product = db.query(models.Product).get(item["product_id"])
        unit_price = float(product.price)
        total += item["quantity"] * unit_price

        sale = models.Sale(
            product_id=item["product_id"],
            quantity=item["quantity"],
            unit_price=unit_price,
            date=datetime.datetime.utcnow()
        )
        sales.append(sale)

        # Decrease inventory
        inventory = db.query(models.Inventory).filter_by(product_id=item["product_id"]).first()
        if inventory:
            inventory.quantity -= item["quantity"]

    order = models.Order(
        customer_name=order_data["customer_name"],
        customer_email=order_data["customer_email"],
        total_amount=total,
        created_at=datetime.datetime.utcnow()
    )
    db.add(order)
    db.flush()  # get order.id

    for s in sales:
        s.order_id = order.id
        db.add(s)

db.commit()
db.close()

print("✅ Demo data successfully populated.")