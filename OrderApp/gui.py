"""gui.py
Простой tkinter-интерфейс для демонстрации: добавление клиентов, создание заказов и просмотр списка.
(Пропущены функции сохранения/загрузки файлов.)

Запускается функцией run_app() — вызывается из main.py.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from models import Customer, Product, Order, OrderItem, ValidationError
from typing import Dict, List
from datetime import datetime


class App:
    """Main application window."""

    def __init__(self, master):
        self.master = master
        master.title("Order Management Prototype")

        # Хранилища в памяти
        self.customers: Dict[str, Customer] = {}
        self.products: Dict[str, Product] = {}
        self.orders: Dict[str, Order] = {}

        # UI
        self._build_ui()

    def _build_ui(self):
        nb = ttk.Notebook(self.master)
        nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        frame_customers = ttk.Frame(nb)
        frame_orders = ttk.Frame(nb)
        frame_products = ttk.Frame(nb)
        nb.add(frame_customers, text="Customers")
        nb.add(frame_products, text="Products")
        nb.add(frame_orders, text="Orders")

        # -- Customers tab
        self._build_customers_tab(frame_customers)

        # -- Products tab
        self._build_products_tab(frame_products)

        # -- Orders tab
        self._build_orders_tab(frame_orders)

    def _build_customers_tab(self, parent):
        frm = ttk.Frame(parent)
        frm.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(frm, text="Name").grid(row=0, column=0)
        self.c_name = ttk.Entry(frm)
        self.c_name.grid(row=0, column=1)

        ttk.Label(frm, text="Email").grid(row=1, column=0)
        self.c_email = ttk.Entry(frm)
        self.c_email.grid(row=1, column=1)

        ttk.Label(frm, text="Phone").grid(row=2, column=0)
        self.c_phone = ttk.Entry(frm)
        self.c_phone.grid(row=2, column=1)

        ttk.Label(frm, text="City").grid(row=3, column=0)
        self.c_city = ttk.Entry(frm)
        self.c_city.grid(row=3, column=1)

        add_btn = ttk.Button(frm, text="Add Customer", command=self.add_customer)
        add_btn.grid(row=4, column=0, columnspan=2, pady=5)

        self.customers_list = tk.Listbox(frm, height=10)
        self.customers_list.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=5)

    def _build_products_tab(self, parent):
        frm = ttk.Frame(parent)
        frm.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(frm, text="Name").grid(row=0, column=0)
        self.p_name = ttk.Entry(frm)
        self.p_name.grid(row=0, column=1)

        ttk.Label(frm, text="Price").grid(row=1, column=0)
        self.p_price = ttk.Entry(frm)
        self.p_price.grid(row=1, column=1)

        add_btn = ttk.Button(frm, text="Add Product", command=self.add_product)
        add_btn.grid(row=2, column=0, columnspan=2, pady=5)

        self.products_list = tk.Listbox(frm, height=10)
        self.products_list.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=5)

    def _build_orders_tab(self, parent):
        frm = ttk.Frame(parent)
        frm.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(frm, text="Customer ID").grid(row=0, column=0)
        self.o_customer_id = ttk.Entry(frm)
        self.o_customer_id.grid(row=0, column=1)

        ttk.Label(frm, text="Product SKU").grid(row=1, column=0)
        self.o_sku = ttk.Entry(frm)
        self.o_sku.grid(row=1, column=1)

        ttk.Label(frm, text="Quantity").grid(row=2, column=0)
        self.o_qty = ttk.Entry(frm)
        self.o_qty.grid(row=2, column=1)

        add_btn = ttk.Button(frm, text="Create Order (1 item)", command=self.create_order)
        add_btn.grid(row=3, column=0, columnspan=2, pady=5)

        self.orders_list = tk.Listbox(frm, height=10)
        self.orders_list.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=5)

    def add_customer(self):
        name = self.c_name.get().strip()
        email = self.c_email.get().strip() or None
        phone = self.c_phone.get().strip() or None
        city = self.c_city.get().strip() or None
        try:
            cust = Customer(name=name, email=email, phone=phone, city=city)
            self.customers[cust.customer_id] = cust
            self.customers_list.insert(tk.END, f"{cust.customer_id} | {cust.name} | {cust.city or '-'}")
            messagebox.showinfo("OK", "Customer added")
        except ValidationError as exc:
            messagebox.showerror("Validation error", str(exc))
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def add_product(self):
        name = self.p_name.get().strip()
        try:
            price = float(self.p_price.get().strip())
        except Exception:
            messagebox.showerror("Error", "Invalid price")
            return
        try:
            prod = Product(name=name, price=price)
            self.products[prod.sku] = prod
            self.products_list.insert(tk.END, f"{prod.sku} | {prod.name} | {prod.price:.2f}")
            messagebox.showinfo("OK", "Product added")
        except ValidationError as exc:
            messagebox.showerror("Validation error", str(exc))
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def create_order(self):
        cid = self.o_customer_id.get().strip()
        sku = self.o_sku.get().strip()
        try:
            qty = int(self.o_qty.get().strip() or 1)
        except Exception:
            messagebox.showerror("Error", "Invalid quantity")
            return
        if cid not in self.customers:
            messagebox.showerror("Error", "Customer not found")
            return
        if sku not in self.products:
            messagebox.showerror("Error", "Product not found")
            return
        try:
            cust = self.customers[cid]
            item = OrderItem(product=self.products[sku], quantity=qty)
            order = Order(customer=cust, items=[item], created_at=datetime.utcnow())
            self.orders[order.order_id] = order
            self.orders_list.insert(tk.END, f"{order.order_id} | {cust.name} | {order.total_cost():.2f}")
            messagebox.showinfo("OK", "Order created")
        except ValidationError as exc:
            messagebox.showerror("Validation error", str(exc))
        except Exception as exc:
            messagebox.showerror("Error", str(exc))


def run_app():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
