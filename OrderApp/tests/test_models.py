"""Unit-тесты для models.py"""

import unittest
from models import Product, Customer, OrderItem, Order, ValidationError
from datetime import datetime


class TestModels(unittest.TestCase):

    def test_product_price_validation(self):
        with self.assertRaises(ValidationError):
            Product(name="X", price=-1.0)

    def test_customer_email_phone_validation(self):
        c = Customer(name="Ivan")
        with self.assertRaises(ValidationError):
            c.email = "not-an-email"
        with self.assertRaises(ValidationError):
            c.phone = "abc"

    def test_order_and_items(self):
        c = Customer(name="Ann", email="a@example.com", phone="+1234567890")
        p = Product(name="Widget", price=10.0)
        item = OrderItem(product=p, quantity=2)
        o = Order(customer=c, items=[item], created_at=datetime.utcnow())
        self.assertEqual(len(c.orders()), 1)
        self.assertAlmostEqual(o.total_cost(), 20.0)


if __name__ == "__main__":
    unittest.main()
