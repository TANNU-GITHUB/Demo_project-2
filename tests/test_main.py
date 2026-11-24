"""Native pytest test suite for MiniStore FastAPI application."""
import pytest
from fastapi.testclient import TestClient
from main import app, calculate_order_total


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def test_products_endpoint_returns_products(client):
    """Verify GET /api/products returns HTTP 200 with list of products."""
    resp = client.get("/api/products")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "name" in data[0]
    assert "price" in data[0]


def test_order_total_calculation_with_discount():
    """Verify 10% discount applied for DISCOUNT10."""
    # 2 items @ $60 = $120. With 10% discount = $108. Free shipping (> $100)
    total = calculate_order_total(60.0, 2, "DISCOUNT10")
    assert total == 108.0


def test_order_total_rejects_negative_price():
    """Verify negative price raises ValueError."""
    with pytest.raises(ValueError, match="Price cannot be negative"):
        calculate_order_total(-10.0, 1)


def test_order_total_rejects_negative_quantity():
    """Verify REQ-2 requirement: quantity <= 0 must raise ValueError('Quantity must be positive').

    [SEEDED BACKEND DEFECT]:
    The implementation in main.py currently computes total without validating quantity > 0,
    failing this test with a negative total rather than raising ValueError!
    """
    with pytest.raises(ValueError, match="Quantity must be positive"):
        calculate_order_total(49.99, -1)


def test_place_order_insufficient_stock(client):
    """Verify placing order for 9999 items returns HTTP 400."""
    resp = client.post("/api/orders", json={"product_id": 1, "quantity": 9999})
    assert resp.status_code == 400
    data = resp.json()
    assert data.get("detail") == "Insufficient stock"
