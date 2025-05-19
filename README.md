# E-commerce Admin API

A FastAPI-based backend for managing products, inventory, sales, and orders for an e-commerce platform.

## Features
- Product management (CRUD, filtering, sorting)
- Inventory management (view, update, low-stock alerts)
- Order creation and listing
- Sales tracking and revenue analytics

## Setup Instructions

### 1. Clone the repository
```powershell
git clone https://github.com/AnasFarooq93/ecommerce-admin-api
cd ecommerce_api
```

### 2. Create and activate a virtual environment (optional but recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

### 3. Install dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables
Edit the `.env` file with your MySQL database credentials:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=ecommerce_db
```

### 5. Run database migrations and populate demo data
```powershell
python app/main.py  # Creates tables on first run
python populate_demo_data.py  # (Optional) Populate demo data
```

### 6. Start the API server
```powershell
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000/`.

## API Endpoints Overview

### Products (`/products`)
- `POST /products/` — Create a new product
- `GET /products/` — List/filter products (by name, SKU, category, price, stock, date, etc.)
- `GET /products/{product_id}` — Get product details

### Inventory (`/inventory`)
- `GET /inventory/` — View/filter inventory (by product, category, SKU, quantity, etc.)
- `GET /inventory/low-stock` — List products with low stock
- `POST /inventory/` — Add or update inventory for a product

### Orders (`/orders`)
- `POST /orders/` — Create a new order (with items)
- `GET /orders/` — List all orders
- `GET /orders/{order_id}` — Get order details

### Sales (`/sales`)
- `POST /sales/` — Record a sale
- `GET /sales/` — List/filter sales (by date, product, category, etc.)
- `GET /sales/revenue-summary` — Revenue summary (daily, weekly, monthly, yearly)
- `GET /sales/compare` — Compare revenue by category or product

## Dependencies
- fastapi
- uvicorn
- sqlalchemy
- pymysql
- python-dotenv
- pydantic

## Notes
- The API uses a MySQL database. Ensure MySQL is running and accessible.
- All endpoints and models are defined in the `app/` directory.
- For demo/testing, use the provided `populate_demo_data.py` script.
- Interactive API docs available at `http://127.0.0.1:8000/docs` after starting the server.
