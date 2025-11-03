"""utils_sort.py
Содержит пользовательскую реализацию сортировки (quicksort) для заказов.
"""

from typing import List
from models import Order
from datetime import datetime


def _order_key_by_date(order: Order):
    return order.created_at


def quicksort_orders(orders: List[Order], key=lambda o: o.created_at, reverse: bool = False) -> List[Order]:
    """
    Быстрая реализация quicksort для списка заказов.
    Служит демонстрацией лямбда-выражений и рекурсии.

    Parameters
    ----------
    orders : list[Order]
    key : callable
        Функция получения ключа для сравнения.
    reverse : bool
        Если True — сортируем по убыванию.

    Returns
    -------
    list[Order]
    """
    if len(orders) <= 1:
        return orders[:]
    pivot = orders[len(orders) // 2]
    pivot_key = key(pivot)
    less = [o for o in orders if key(o) < pivot_key]
    equal = [o for o in orders if key(o) == pivot_key]
    greater = [o for o in orders if key(o) > pivot_key]
    result = quicksort_orders(less, key, reverse) + equal + quicksort_orders(greater, key, reverse)
    if reverse:
        result.reverse()
    return result
