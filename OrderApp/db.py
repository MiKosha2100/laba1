"""db.py
Простейшая обёртка над SQLite (in-memory по умолчанию).
Пропущены функции импорта/экспорта в CSV/JSON (по заданию).
"""

import sqlite3
from typing import Optional, List, Tuple
from contextlib import closing
from datetime import datetime


class SimpleDB:
    """
    Простой менеджер SQLite соединения.

    Parameters
    ----------
    path : str
        Путь к файлу БД. Если ':memory:' — in-memory база.
    """

    def __init__(self, path: str = ":memory:"):
        self.path = path
        self.conn = sqlite3.connect(self.path, detect_types=sqlite3.PARSE_DECLTYPES)
        self._init_schema()

    def _init_schema(self):
        """Создать базовую схему: customers, products, orders, order_items."""
        with closing(self.conn.cursor()) as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                city TEXT
            )
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                sku TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
            )
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                sku TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(order_id),
                FOREIGN KEY(sku) REFERENCES products(sku)
            )
            """)
            self.conn.commit()

    def insert_customer(self, customer_id: str, name: str, email: Optional[str], phone: Optional[str], city: Optional[str]):
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO customers(customer_id, name, email, phone, city) VALUES (?, ?, ?, ?, ?)",
                    (customer_id, name, email, phone, city)
                )
        except Exception as exc:
            # Простая обработка ошибок
            raise RuntimeError(f"Failed to insert customer: {exc}")

    def list_customers(self) -> List[Tuple]:
        cur = self.conn.cursor()
        cur.execute("SELECT customer_id, name, email, phone, city FROM customers")
        return cur.fetchall()

    def close(self):
        self.conn.close()
