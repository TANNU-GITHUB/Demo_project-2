"""MiniStore FastAPI Web Application with SQLite Database."""
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from jinja2 import Template

from models import (
    get_all_products,
    get_product_by_id,
    init_db,
    update_product_stock,
    create_order_record,
)

app = FastAPI(title="MiniStore")
init_db()

# Mount static assets
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

TEMPLATE_FILE = Path(__file__).parent / "templates" / "index.html"


def calculate_order_total(price: float, quantity: int, discount_code: str = "") -> float:
    """Calculate order total with discounts and shipping.

    SPECIFICATION (REQ-2):
    - Price cannot be negative (raise ValueError('Price cannot be negative')).
    - Quantity must be strictly positive (> 0); non-positive must raise
      ValueError('Quantity must be positive').
    - DISCOUNT10 applies 10% discount.
    - Free shipping over $100 after discount, else $5 shipping.
    """
    if price < 0:
        raise ValueError("Price cannot be negative")

    # [SEEDED BACKEND DEFECT]: Missing quantity validation!
    # According to REQ-2, quantity <= 0 must raise ValueError("Quantity must be positive").
    # Defect allows negative quantities, calculating negative totals (e.g. price 49.99 * -2 = -99.98).
    subtotal = price * quantity

    if discount_code == "DISCOUNT10":
        subtotal *= 0.90

    shipping = 0.0 if subtotal > 100.0 else 5.0
    return round(subtotal + shipping, 2)


class OrderRequest(BaseModel):
    product_id: int
    quantity: int = 1
    discount_code: Optional[str] = ""


@app.get("/", response_class=HTMLResponse)
def index():
    """Storefront home page rendering inventory."""
    products = get_all_products()
    html_content = TEMPLATE_FILE.read_text(encoding="utf-8")
    template = Template(html_content)
    return HTMLResponse(content=template.render(products=products))


@app.get("/api/products")
def list_products():
    """Return all products in inventory."""
    return get_all_products()


@app.post("/api/orders", status_code=201)
def place_order(order: OrderRequest):
    """Place an order for a product."""
    product = get_product_by_id(order.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if order.quantity > product["stock"]:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    try:
        total = calculate_order_total(product["price"], order.quantity, order.discount_code or "")
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))

    new_stock = product["stock"] - order.quantity
    update_product_stock(order.product_id, new_stock)
    order_id = create_order_record(order.product_id, order.quantity, total)

    return {
        "order_id": order_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "total": total,
        "status": "confirmed",
    }


@app.get("/analytics")
def analytics():
    """Store metrics report.

    [SEEDED FRONTEND / BROWSER DEFECT]:
    Calling this route raises an uncaught 500 error due to division by zero,
    causing browser test failure and generating a failure screenshot.
    """
    total_orders = 0
    # Bug: Division by zero when calculating average order value with 0 orders
    avg_value = 100 / total_orders
    return {"average_order_value": avg_value}


@app.get("/health")
def health():
    return {"status": "ok"}
