from fastapi import FastAPI
from app.database import Base, engine
from app.routers import products, inventory, sales, orders

app = FastAPI()

# Create all DB tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(sales.router)
app.include_router(orders.router)

@app.get("/")
def read_root():
    return {"message": "E-commerce Admin API is live"}