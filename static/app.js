// MiniStore Frontend JavaScript

// [SEEDED FRONTEND BUG]:
// Uncaught ReferenceError on window load when initializing tracker
try {
    initUserTracker(); // ReferenceError: initUserTracker is not defined
} catch (e) {
    console.error("Frontend tracker failure:", e);
}

// Function to handle buying a product via valid endpoint
async function handleQuickOrder(productId) {
    const qtyInput = document.getElementById(`qty-${productId}`);
    const quantity = parseInt(qtyInput ? qtyInput.value : 1, 10);
    const resultBox = document.getElementById("order-result");

    try {
        const response = await fetch("/api/orders", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ product_id: productId, quantity: quantity }),
        });
        const data = await response.json();

        if (response.ok) {
            resultBox.innerHTML = `<div class="success">Order #${data.order_id} placed! Total: $${data.total}</div>`;
            const stockSpan = document.getElementById(`stock-${productId}`);
            if (stockSpan) stockSpan.textContent = parseInt(stockSpan.textContent) - quantity;
        } else {
            resultBox.innerHTML = `<div class="error">Order failed: ${data.error}</div>`;
        }
    } catch (err) {
        resultBox.innerHTML = `<div class="error">Network error: ${err.message}</div>`;
    }
}

// [SEEDED CONSISTENCY BUG]:
// Frontend calls "/api/checkout", but the backend Flask router only defines "/api/orders"!
// The cross-layer consistency check will detect this as a `missing_route` finding!
async function submitCheckout() {
    const discountCode = document.getElementById("discount-code").value;
    const resultBox = document.getElementById("order-result");

    try {
        // Mismatched URL: backend does not have /api/checkout
        const response = await fetch("/api/checkout", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ discount_code: discountCode }),
        });
        const data = await response.json();
        resultBox.textContent = JSON.stringify(data);
    } catch (err) {
        resultBox.innerHTML = `<div class="error">Checkout error: ${err.message}</div>`;
    }
}

// Another mismatched endpoint: DELETE /api/products/delete (backend has no such route or DELETE method)
async function removeProduct(productId) {
    await fetch("/api/products/delete", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: productId }),
    });
}
