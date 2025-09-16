#!/usr/bin/env python3
"""
Sensor Data Logger Database
File: sensor_logger.py
Author: Ifenkwe Agape Ifeanyichukwu
Matric Number: BU22MCT1036
Description: A menu-driven database system for logging sensor readings.
             Supports add, view, update, delete, and export to CSV.
             Data is stored in sensor_data.db using SQLite.
"""

import sqlite3
import datetime
import csv
import os

DB_FILENAME = "sensor_data.db"


# -----------------------
# Database handler class
# -----------------------
class SensorDB:
    def __init__(self, db_file=DB_FILENAME):
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            """)

    def add_reading(self, sensor_name, value, unit, timestamp=None, status="Normal"):
        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.conn:
            cursor = self.conn.execute("""
                INSERT INTO sensor_data (sensor_name, value, unit, timestamp, status)
                VALUES (?, ?, ?, ?, ?)
            """, (sensor_name.strip(), value, unit.strip(), timestamp, status.strip()))
        return cursor.lastrowid

    def get_all_readings(self):
        cursor = self.conn.execute("SELECT * FROM sensor_data ORDER BY id")
        return cursor.fetchall()

    def get_reading(self, reading_id):
        cursor = self.conn.execute("SELECT * FROM sensor_data WHERE id = ?", (reading_id,))
        return cursor.fetchone()

    def update_reading(self, reading_id, sensor_name, value, unit, timestamp, status):
        with self.conn:
            cursor = self.conn.execute("""
                UPDATE sensor_data
                SET sensor_name=?, value=?, unit=?, timestamp=?, status=?
                WHERE id=?
            """, (sensor_name.strip(), value, unit.strip(), timestamp.strip(), status.strip(), reading_id))
        return cursor.rowcount > 0

    def delete_reading(self, reading_id):
        with self.conn:
            cursor = self.conn.execute("DELETE FROM sensor_data WHERE id=?", (reading_id,))
        return cursor.rowcount > 0

    def export_to_csv(self, csv_path="sensor_log.csv"):
        rows = self.get_all_readings()
        if not rows:
            raise ValueError("No sensor data to export.")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "sensor_name", "value", "unit", "timestamp", "status"])
            for r in rows:
                writer.writerow([r["id"], r["sensor_name"], r["value"], r["unit"], r["timestamp"], r["status"]])

    def close(self):
        self.conn.close()


# -----------------------
# Helper functions
# -----------------------
def input_nonempty(prompt):
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("⚠ Input cannot be empty.")

def input_float(prompt):
    while True:
        try:
            return float(input(prompt).strip())
        except ValueError:
            print("⚠ Please enter a valid number.")

def confirm(prompt):
    return input(prompt + " (y/n): ").strip().lower() in ("y", "yes")


def print_reading(row):
    print(f"ID: {row['id']}")
    print(f"  Sensor   : {row['sensor_name']}")
    print(f"  Value    : {row['value']} {row['unit']}")
    print(f"  Time     : {row['timestamp']}")
    print(f"  Status   : {row['status']}")
    print("-" * 40)


# -----------------------
# Menu functions
# -----------------------
def add_reading_flow(db):
    print("\n-- Add Sensor Reading --")
    sensor_name = input_nonempty("Sensor name: ")
    value = input_float("Sensor value: ")
    unit = input_nonempty("Unit (e.g., °C, kPa, m/s²): ")
    status = input_nonempty("Status (Normal/Warning/Error): ")
    rid = db.add_reading(sensor_name, value, unit, status=status)
    print(f"✅ Reading added with ID {rid}")

def view_readings_flow(db):
    rows = db.get_all_readings()
    if not rows:
        print("📭 No sensor readings found.")
        return
    for r in rows:
        print_reading(r)

def update_reading_flow(db):
    rid = int(input("Enter reading ID to update: "))
    row = db.get_reading(rid)
    if not row:
        print("⚠ Reading not found.")
        return
    print("Current values:")
    print_reading(row)
    sensor_name = input_nonempty(f"New sensor name [{row['sensor_name']}]: ") or row['sensor_name']
    value = input_float(f"New value [{row['value']}]: ") or row['value']
    unit = input_nonempty(f"New unit [{row['unit']}]: ") or row['unit']
    status = input_nonempty(f"New status [{row['status']}]: ") or row['status']
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if db.update_reading(rid, sensor_name, value, unit, timestamp, status):
        print("✅ Reading updated successfully.")
    else:
        print("⚠ Failed to update reading.")

def delete_reading_flow(db):
    rid = int(input("Enter reading ID to delete: "))
    row = db.get_reading(rid)
    if not row:
        print("⚠ Reading not found.")
        return
    print_reading(row)
    if confirm("Are you sure you want to delete this reading?"):
        if db.delete_reading(rid):
            print("🗑 Deleted successfully.")
        else:
            print("⚠ Could not delete reading.")

def export_flow(db):
    path = input("Enter CSV filename [default: sensor_log.csv]: ").strip() or "sensor_log.csv"
    try:
        db.export_to_csv(path)
        print(f"✅ Data exported to {path}")
    except ValueError as e:
        print("⚠", e)


# -----------------------
# Main Menu
# -----------------------
def menu():
    db = SensorDB()
    try:
        while True:
            print("""
--- Sensor Data Logger ---
1. Add Sensor Reading
2. View All Readings
3. Update Reading
4. Delete Reading
5. Export to CSV
6. Exit
""")
            choice = input("Choose an option (1-6): ").strip()
            if choice == "1":
                add_reading_flow(db)
            elif choice == "2":
                view_readings_flow(db)
            elif choice == "3":
                update_reading_flow(db)
            elif choice == "4":
                delete_reading_flow(db)
            elif choice == "5":
                export_flow(db)
            elif choice == "6":
                print("👋 Exiting program...")
                break
            else:
                print("⚠ Invalid choice, try again.")
    finally:
        db.close()


if __name__ == "__main__":
    menu()




