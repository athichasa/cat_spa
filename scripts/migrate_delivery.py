import sqlite3
import os

db_paths = [
    "cat_spa.db",
    r"C:\Users\Admin\Downloads\cat_spa\cat_spa.db",
    r"C:\Users\Admin\Downloads\cat_spa\cat_spa\cat_spa.db"
]

new_cols = [
    ("delivery_type", "TEXT DEFAULT 'none'"),
    ("delivery_fee", "REAL DEFAULT 0"),
    ("pickup_address", "TEXT DEFAULT ''"),
    ("latitude", "REAL DEFAULT NULL"),
    ("longitude", "REAL DEFAULT NULL"),
    ("delivery_notes", "TEXT DEFAULT ''")
]

for db_path in db_paths:
    if not os.path.exists(db_path):
        continue
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    existing_cols = [r[1] for r in cur.execute("PRAGMA table_info(bookings)").fetchall()]
    print(f"Database: {db_path} (Existing cols: {len(existing_cols)})")
    
    for col_name, col_type in new_cols:
        if col_name not in existing_cols:
            cur.execute(f"ALTER TABLE bookings ADD COLUMN {col_name} {col_type}")
            print(f"  + Added column {col_name} ({col_type})")
        else:
            print(f"  = Column {col_name} already present")
            
    con.commit()
    con.close()

print("All databases migrated successfully!")
