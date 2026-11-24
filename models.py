"""SQLite Database Models & Helpers for MiniStore."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "store.db"


def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    """)

    # Seed default products if empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
            [
                ("Wireless Keyboard", 49.99, 15),
                ("Ergonomic Mouse", 29.99, 25),
                ("USB-C Hub", 19.99, 10),
                ("Desk Mat", 14.99, 50),
            ],
        )
    conn.commit()
    conn.close()


def get_all_products():
    conn = get_db_connection()
    products = conn.execute("SELECT id, name, price, stock FROM products").fetchall()
    conn.close()
    return [dict(p) for p in products]


def get_product_by_id(product_id: int):
    conn = get_db_connection()
    product = conn.execute(
        "SELECT id, name, price, stock FROM products WHERE id = ?", (product_id,)
    ).fetchone()
    conn.close()
    return dict(product) if product else None


def update_product_stock(product_id: int, new_stock: int):
    conn = get_db_connection()
    conn.execute(
        "UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id)
    )
    conn.commit()
    conn.close()


def create_order_record(product_id: int, quantity: int, total: float):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (product_id, quantity, total) VALUES (?, ?, ?)",
        (product_id, quantity, total),
    )
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return order_id
