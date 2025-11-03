"""models.py
Классы данных: Product, Person -> Customer, Order, OrderItem.

Докстринги в стиле numpydoc.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import List, Optional
import uuid


EMAIL_RE = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
PHONE_RE = re.compile(r"^\+?\d{7,15}$")


def _generate_id() -> str:
    """Генерирует уникальный ID для объектов."""
    return uuid.uuid4().hex


class ValidationError(ValueError):
    """Ошибка валидации данных."""
    pass


@dataclass
class Product:
    """
    Класс продукта.

    Parameters
    ----------
    name : str
        Название товара.
    price : float
        Цена за единицу (>= 0).
    sku : str, optional
        Артикул; если не указан генерируется автоматически.
    """
    name: str
    price: float
    sku: Optional[str] = None

    def __post_init__(self):
        if self.price < 0:
            raise ValidationError("Price cannot be negative")
        if not self.sku:
            self.sku = _generate_id()

    def __repr__(self):
        return f"Product(name={self.name!r}, price={self.price:.2f}, sku={self.sku})"


class Person:
    """
    Базовый класс для людей.

    Implements basic contact storage and validation.
    """

    def __init__(self, name: str, email: Optional[str] = None, phone: Optional[str] = None):
        self._name = name
        self._email = None
        self._phone = None
        if email:
            self.email = email
        if phone:
            self.phone = phone

    @property
    def name(self) -> str:
        """Имя человека."""
        return self._name

    @property
    def email(self) -> Optional[str]:
        return self._email

    @email.setter
    def email(self, value: str):
        if not EMAIL_RE.match(value):
            raise ValidationError(f"Invalid email: {value}")
        self._email = value

    @property
    def phone(self) -> Optional[str]:
        return self._phone

    @phone.setter
    def phone(self, value: str):
        if not PHONE_RE.match(value):
            raise ValidationError(f"Invalid phone number: {value}")
        self._phone = value

    def contact_summary(self) -> str:
        """Возвращает строку с контактами (полиморфизм: может быть переопределён)."""
        return f"{self._name} | email: {self._email or '—'} | phone: {self._phone or '—'}"


class Customer(Person):
    """
    Представление клиента интернет-магазина.

    Parameters
    ----------
    name : str
        Имя клиента.
    email : str
        Email.
    phone : str
        Телефон.
    city : str, optional
        Город клиента.
    customer_id : str, optional
        Идентификатор клиента.
    """

    def __init__(self, name: str, email: Optional[str] = None, phone: Optional[str] = None, city: Optional[str] = None, customer_id: Optional[str] = None):
        super().__init__(name, email, phone)
        self.city = city
        self.customer_id = customer_id or _generate_id()
        self._orders: List["Order"] = []

    def add_order(self, order: "Order"):
        """Добавить заказ к клиенту (инкапсуляция: скрываем прямую манипуляцию со списком)."""
        self._orders.append(order)

    def orders(self) -> List["Order"]:
        """Вернуть копию списка заказов клиента."""
        return list(self._orders)

    def total_spent(self) -> float:
        """Посчитать общую сумму, потраченную клиентом."""
        return sum(o.total_cost() for o in self._orders)

    def contact_summary(self) -> str:
        """Переопределение (полиморфизм): дополнить контакт информацией о заказах."""
        return f"{self._name} ({self.customer_id}) — orders: {len(self._orders)} — {super().contact_summary()}"


@dataclass
class OrderItem:
    """
    Элемент заказа: товар + количество.

    Parameters
    ----------
    product : Product
        Объект товара.
    quantity : int
        Количество (>0).
    """
    product: Product
    quantity: int = 1

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be > 0")

    def cost(self) -> float:
        """Стоимость позиции."""
        return self.product.price * self.quantity


class Order:
    """
    Класс заказа.

    Parameters
    ----------
    customer : Customer
        Клиент, оформивший заказ.
    items : List[OrderItem], optional
        Список позиций.
    created_at : datetime, optional
        Дата создания заказа.
    order_id : str, optional
        Идентификатор заказа.
    """

    def __init__(self, customer: Customer, items: Optional[List[OrderItem]] = None, created_at: Optional[datetime] = None, order_id: Optional[str] = None):
        self.order_id = order_id or _generate_id()
        self.customer = customer
        self._items: List[OrderItem] = items[:] if items else []
        self.created_at = created_at or datetime.utcnow()
        # Зарегистрируем заказ у клиента
        try:
            customer.add_order(self)
        except Exception:
            # Не поднимаем детальную ошибку — важна устойчивость
            pass

    def add_item(self, item: OrderItem):
        """Добавить позицию в заказ."""
        self._items.append(item)

    def items(self) -> List[OrderItem]:
        """Вернуть копию списка позиций."""
        return list(self._items)

    def total_cost(self) -> float:
        """Посчитать полную стоимость заказа."""
        return sum(i.cost() for i in self._items)

    def __repr__(self):
        return f"Order(id={self.order_id}, customer={self.customer.name}, items={len(self._items)}, total={self.total_cost():.2f})"
