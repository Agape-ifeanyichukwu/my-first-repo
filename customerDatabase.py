#!/usr/bin/env python3
"""
Order Database Management System
File: order_database.py
Author: Ifenkwe Agape Ifeanyichukwu
Matric Number: BU22MCT1036
Description: Simple menu-driven order DB using SQLite. Supports add, view,
             update, delete, and export to CSV. Data persists in orders.db.
"""

import sqlite3
import datetime
import csv
import os
from typing import Optional, Tuple, List

DB_FILENAME = "orders.db"


# -----------------------
# Database helper class
# -----------------------
class OrderDB:
    def __init__(self, db_file: str = DB_FILENAME):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self) -> None:
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT NOT NULL,
                    product TEXT NOT NULL,
                    quantity INTEGER NOT NULL CHECK(quantity > 0),
                    unit_price REAL NOT NULL CHECK(unit_price >= 0),
                    order_date TEXT NOT NULL,
                    status TEXT NOT NULL
                )
                """
            )

    def add_order(
        self,
        customer_name: str,
        product: str,
        quantity: int,
        unit_price: float,
        order_date: Optional[str] = None,
        status: str = "pending",
    ) -> int:
        if order_date is None:
            order_date = datetime.date.today().isoformat()
        with self.conn:
            cursor = self.conn.execute(
                """
                INSERT INTO orders (customer_name, product, quantity, unit_price, order_date, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (customer_name.strip(), product.strip(), quantity, unit_price, order_date, status.strip()),
            )
        return cursor.lastrowid

    def get_all_orders(self) -> List[sqlite3.Row]:
        cursor = self.conn.execute("SELECT * FROM orders ORDER BY id")
        return cursor.fetchall()

    def get_order(self, order_id: int) -> Optional[sqlite3.Row]:
        cursor = self.conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        return cursor.fetchone()

    def update_order(
        self,
        order_id: int,
        customer_name: str,
        product: str,
        quantity: int,
        unit_price: float,
        order_date: str,
        status: str,
    ) -> bool:
        with self.conn:
            cursor = self.conn.execute(
                """
                UPDATE orders
                SET customer_name = ?, product = ?, quantity = ?, unit_price = ?, order_date = ?, status = ?
                WHERE id = ?
                """,
                (customer_name.strip(), product.strip(), quantity, unit_price, order_date.strip(), status.strip(), order_id),
            )
        return cursor.rowcount > 0

    def delete_order(self, order_id: int) -> bool:
        with self.conn:
            cursor = self.conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        return cursor.rowcount > 0

    def export_to_csv(self, csv_path: str) -> None:
        rows = self.get_all_orders()
        if not rows:
            raise ValueError("No orders to export.")
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "customer_name", "product", "quantity", "unit_price", "order_date", "status"])
            for r in rows:
                writer.writerow([r["id"], r["customer_name"], r["product"], r["quantity"], r["unit_price"], r["order_date"], r["status"]])

    def close(self) -> None:
        if self.conn:
            self.conn.close()


# -----------------------
# Input helpers
# -----------------------
def input_nonempty(prompt: str) -> str:
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("Input cannot be empty. Please try again.")


def input_int(prompt: str, min_value: Optional[int] = None) -> int:
    while True:
        s = input(prompt).strip()
        try:
            v = int(s)
            if min_value is not None and v < min_value:
                print(f"Value must be at least {min_value}.")
                continue
            return v
        except ValueError:
            print("Please enter a valid integer.")


def input_float(prompt: str, min_value: Optional[float] = None) -> float:
    while True:
        s = input(prompt).strip()
        try:
            v = float(s)
            if min_value is not None and v < min_value:
                print(f"Value must be at least {min_value}.")
                continue
            return v
        except ValueError:
            print("Please enter a valid number (e.g., 1500 or 1500.00).")


def input_date(prompt: str, default_iso: Optional[str] = None) -> str:
    while True:
        s = input(prompt).strip()
        if not s and default_iso:
            return default_iso
        try:
            # Accept YYYY-MM-DD
            parsed = datetime.date.fromisoformat(s)
            return parsed.isoformat()
        except Exception:
            print("Please enter a valid date in YYYY-MM-DD format or leave blank for today.")


def confirm(prompt: str) -> bool:
    while True:
        resp = input(f"{prompt} (y/n): ").strip().lower()
        if resp in ("y", "yes"):
            return True
        if resp in ("n", "no"):
            return False
        print("Please answer y or n.")


# -----------------------
# Display helpers
# -----------------------
def print_order_row(row: sqlite3.Row) -> None:
    print(f"ID: {row['id']}")
    print(f"  Customer : {row['customer_name']}")
    print(f"  Product  : {row['product']}")
    print(f"  Quantity : {row['quantity']}")
    print(f"  UnitPrice: {row['unit_price']}")
    print(f"  Date     : {row['order_date']}")
    print(f"  Status   : {row['status']}")
    print("-" * 40)


def list_orders(db: OrderDB) -> None:
    rows = db.get_all_orders()
    if not rows:
        print("No orders found.")
        return
    print(f"\nFound {len(rows)} order(s):\n" + "=" * 40)
    for r in rows:
        print_order_row(r)


# -----------------------
# Menu & flows
# -----------------------
def add_order_flow(db: OrderDB) -> None:
    print("\n-- Add New Order --")
    customer = input_nonempty("Customer name: ")
    product = input_nonempty("Product name: ")
    quantity = input_int("Quantity (integer > 0): ", min_value=1)
    unit_price = input_float("Unit price (e.g., 5000): ", min_value=0.0)
    today = datetime.date.today().isoformat()
    order_date = input_date(f"Order date [YYYY-MM-DD] (leave blank for {today}): ", default_iso=today)
    status = input_nonempty("Status (e.g., pending, shipped, cancelled) [default 'pending']: ") or "pending"
    order_id = db.add_order(customer, product, quantity, unit_price, order_date, status)
    print(f"✅ Order added with ID {order_id}.")


def view_orders_flow(db: OrderDB) -> None:
    print("\n-- View Orders --")
    list_orders(db)


def update_order_flow(db: OrderDB) -> None:
    print("\n-- Update Order --")
    order_id = input_int("Enter order ID to update: ", min_value=1)
    existing = db.get_order(order_id)
    if not existing:
        print("Order not found.")
        return
    print("Current values:")
    print_order_row(existing)
    print("Enter new values (leave blank to keep current value).")

    def maybe(prompt: str, current_val: str) -> str:
        s = input(f"{prompt} [{current_val}]: ").strip()
        return s if s else current_val

    new_customer = maybe("Customer name", existing["customer_name"])
    new_product = maybe("Product name", existing["product"])

    # quantity
    while True:
        q_raw = input(f"Quantity [{existing['quantity']}]: ").strip()
        if not q_raw:
            new_quantity = existing["quantity"]
            break
        try:
            q = int(q_raw)
            if q <= 0:
                print("Quantity must be > 0.")
                continue
            new_quantity = q
            break
        except ValueError:
            print("Please enter a valid integer.")

    # unit price
    while True:
        p_raw = input(f"Unit price [{existing['unit_price']}]: ").strip()
        if not p_raw:
            new_price = existing["unit_price"]
            break
        try:
            p = float(p_raw)
            if p < 0:
                print("Price cannot be negative.")
                continue
            new_price = p
            break
        except ValueError:
            print("Please enter a valid number.")

    today_iso = datetime.date.today().isoformat()
    new_date = input_date(f"Order date [{existing['order_date']}] (YYYY-MM-DD, leave blank to keep): ", default_iso=existing["order_date"])
    new_status = input(f"Status [{existing['status']}]: ").strip() or existing["status"]

    updated = db.update_order(order_id, new_customer, new_product, new_quantity, new_price, new_date, new_status)
    if updated:
        print("✅ Order updated successfully.")
    else:
        print("⚠️ Failed to update order (no changes made?).")


def delete_order_flow(db: OrderDB) -> None:
    print("\n-- Delete Order --")
    order_id = input_int("Enter order ID to delete: ", min_value=1)
    existing = db.get_order(order_id)
    if not existing:
        print("Order not found.")
        return
    print("Order to be deleted:")
    print_order_row(existing)
    if confirm("Are you sure you want to delete this order?"):
        if db.delete_order(order_id):
            print("✅ Order deleted.")
        else:
            print("⚠️ Could not delete order.")
    else:
        print("Deletion cancelled.")


def export_flow(db: OrderDB) -> None:
    print("\n-- Export Orders to CSV --")
    default_path = os.path.join(os.getcwd(), "orders_export.csv")
    path = input(f"CSV file path [default: {default_path}]: ").strip() or default_path
    try:
        db.export_to_csv(path)
        print(f"✅ Exported orders to {path}")
    except ValueError as e:
        print("⚠️", e)
    except Exception as e:
        print("An error occurred while exporting:", e)


def menu_loop() -> None:
    db = OrderDB()
    try:
        while True:
            print(
                """
--- Order Database Menu ---
1. Add Order
2. View Orders
3. Update Order
4. Delete Order
5. Export orders to CSV
6. Exit
"""
            )
            choice = input("Choose an option (1-6): ").strip()
            if choice == "1":
                add_order_flow(db)
            elif choice == "2":
                view_orders_flow(db)
            elif choice == "3":
                update_order_flow(db)
            elif choice == "4":
                delete_order_flow(db)
            elif choice == "5":
                export_flow(db)
            elif choice == "6":
                print("Goodbye 👋")
                break
            else:
                print("Invalid choice — enter a number between 1 and 6.")
    except KeyboardInterrupt:
        print("\nInterrupted — exiting.")
    finally:
        db.close()


# -----------------------
# Entry point
# -----------------------
if __name__ == "__main__":
    menu_loop()
