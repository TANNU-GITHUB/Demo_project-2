# MiniStore — Test Target Project for AI Testing Agent

A lightweight Flask web application with an SQLite database and a browser frontend, specially designed to test all capabilities of the AI Full-Stack Testing Agent.

## Architecture

- **Backend:** Flask web service in `app.py` with routes, business logic, and API endpoints.
- **Database:** SQLite (`store.db`) managed via `models.py` with `products` and `orders` tables.
- **Frontend:** Jinja2 template in `templates/index.html` styled with `static/style.css` and interactive JavaScript in `static/app.js`.
- **Specification:** Formal natural language requirements in `spec.txt`.
- **Tests:** Native pytest test suite in `tests/test_app.py`.

## Seeded Defects for Agent Testing

This project contains intentional defects across every layer so you can verify that the testing agent catches them:

1. **Backend Logic Defect (`app.py` - `calculate_order_total`):**
   - **Requirement (REQ-2):** "Quantity must be strictly positive (> 0); non-positive must raise ValueError('Quantity must be positive')."
   - **Defect:** Missing `quantity <= 0` validation. When called with negative quantity (e.g. `-1`), it calculates negative totals (`price * -1`) instead of raising `ValueError`.
   - **Detected by:** Native Pytest stage (T006), White-Box / Black-Box test generation stages, and Requirement Traceability.

2. **Frontend / Browser Defect (`app.py` - `/analytics` & `static/app.js`):**
   - **Requirement (REQ-5):** "The route GET /analytics must display store summary statistics."
   - **Defect:** Accessing `/analytics` triggers a ZeroDivisionError (500 Internal Server Error) when calculating average order value with zero orders. Additionally, `static/app.js` has an unhandled tracker error.
   - **Detected by:** Playwright Browser Automation stage (T008) which navigates discovered routes, detects HTTP 500 failure, and captures failure screenshots and traces in `browser_artifacts/` (T012).

3. **Cross-Layer Consistency Defect (`static/app.js` vs `app.py`):**
   - **Requirement (REQ-3 & REQ-6):** Checkout endpoint is `POST /api/orders`.
   - **Defect:** `static/app.js` calls `POST /api/checkout` and `DELETE /api/products/delete`. Neither route exists in `app.py`.
   - **Detected by:** Cross-Layer Consistency stage (T011) which reports `missing_route` findings with exact source line numbers in both frontend JavaScript and backend routes.

## How to Test with the Agent

1. **Upload via Live Lab:**
   - In Live Lab, load `app.py` as source code and `spec.txt` as requirements document.
   - Run the analysis pipeline to see White-box, Black-box, Coverage, and Defect Detection.

2. **Full-Project Repository Testing:**
   - Push or connect this directory to a GitHub repository or test via the Full-Project Agent API (`POST /api/github/full-project`).
   - The agent will run all 11 stages: staging, framework detection, cross-layer inventory, native pytest, HTTP integration tests, Playwright browser tests, Jev semantic checks, trace data flow, consistency checks, screenshot collection, and report generation!
