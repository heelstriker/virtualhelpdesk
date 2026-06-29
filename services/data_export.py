import os
import sqlite3
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "..", "database", "inventory.db")
)

EXPORT_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "exports")
)

os.makedirs(EXPORT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

tables = [
    "devices",
    "hardware",
    "software",
    "patches",
    "printers"
]

for table in tables:

    cursor.execute(f"SELECT * FROM {table}")

    rows = cursor.fetchall()

    headers = [c[0] for c in cursor.description]

    csv_path = os.path.join(
        EXPORT_DIR,
        f"{table}.csv"
    )

    with open(
        csv_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow(headers)

        writer.writerows(rows)

    print(f"Exported {csv_path}")

conn.close()