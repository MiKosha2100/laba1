"""analysis.py
Функции анализа и визуализации данных.
Использует pandas, matplotlib и networkx.
"""

import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from typing import List, Dict, Any
from collections import Counter
from datetime import datetime


def top_n_clients_by_orders(orders: List[Dict[str, Any]], n: int = 5) -> pd.DataFrame:
    """
    Топ N клиентов по количеству заказов.

    Parameters
    ----------
    orders : list of dict
        Каждый заказ — словарь с ключом 'customer_id'.
    n : int
        Количество топов.

    Returns
    -------
    DataFrame
        DataFrame с колонками ['customer_id', 'orders_count'].
    """
    df = pd.DataFrame(orders)
    if 'customer_id' not in df.columns:
        return pd.DataFrame(columns=['customer_id', 'orders_count'])
    counts = df['customer_id'].value_counts().rename_axis('customer_id').reset_index(name='orders_count')
    return counts.head(n)


def orders_over_time(orders: List[Dict[str, Any]], date_field: str = 'created_at') -> pd.Series:
    """
    Возвращает Series с количеством заказов по датам (date index).

    Parameters
    ----------
    orders : list of dict
        Каждый заказ содержит поле date_field (datetime or ISO string).
    date_field : str
        Имя поля с датой.

    Returns
    -------
    pd.Series
        Series indexed by date (pd.Timestamp.date) with counts.
    """
    df = pd.DataFrame(orders)
    if date_field not in df.columns:
        return pd.Series(dtype=int)
    # Попробуем привести к datetime
    df[date_field] = pd.to_datetime(df[date_field])
    df['date'] = df[date_field].dt.date
    counts = df.groupby('date').size()
    return counts


def plot_orders_over_time(series: pd.Series, ax=None):
    """
    Построить график динамики заказов.

    Parameters
    ----------
    series : pd.Series
        Series с индексом дат и значениями — количеством заказов.
    ax : matplotlib.axes.Axes, optional
        Ось для рисования.
    """
    if ax is None:
        fig, ax = plt.subplots()
    series.plot(ax=ax)
    ax.set_title("Orders over time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of orders")
    return ax


def build_customer_product_graph(orders: List[Dict[str, Any]]) -> nx.Graph:
    """
    Построить bipartite-граф клиентов и товаров на основе заказов.

    Parameters
    ----------
    orders : list of dict
        Каждый заказ должен иметь 'customer_id' и 'items' (list of {'sku':..., 'quantity':...})

    Returns
    -------
    networkx.Graph
        Непомеченный граф, где клиенты и товары соединены.
    """
    G = nx.Graph()
    for o in orders:
        cid = o.get('customer_id')
        if not cid:
            continue
        G.add_node(f"c:{cid}", type='customer')
        for it in o.get('items', []):
            sku = it.get('sku')
            if not sku:
                continue
            G.add_node(f"p:{sku}", type='product')
            # вес можно учитывать по количеству
            q = it.get('quantity', 1)
            if G.has_edge(f"c:{cid}", f"p:{sku}"):
                G[f"c:{cid}"][f"p:{sku}"]['weight'] += q
            else:
                G.add_edge(f"c:{cid}", f"p:{sku}", weight=q)
    return G


def top_k_products_by_sales(orders: List[Dict[str, Any]], k: int = 5) -> pd.DataFrame:
    """
    Топ k продуктов по суммарному количеству (quantity).

    Parameters
    ----------
    orders : list of dict
    k : int

    Returns
    -------
    DataFrame
        ['sku', 'quantity']
    """
    counter = Counter()
    for o in orders:
        for it in o.get('items', []):
            sku = it.get('sku')
            q = it.get('quantity', 1)
            if sku:
                counter[sku] += q
    df = pd.DataFrame(counter.items(), columns=['sku', 'quantity']).sort_values('quantity', ascending=False)
    return df.head(k)
