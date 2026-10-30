import sqlite3
import os

dbs = [
    r'c:\Users\Admin\.gemini\antigravity\scratch\cat_spa\cat_spa.db',
    r'C:\Users\Admin\Downloads\cat_spa\cat_spa.db',
    r'C:\Users\Admin\Downloads\cat_spa\cat_spa\cat_spa.db'
]

new_columns = [
    ("distance_km", "REAL DEFAULT 0"),
    ("payment_method", "TEXT DEFAULT 'pay_at_shop'"),
    ("payment_status", "TEXT DEFAULT 'รอชำระหน้าร้าน'"),
    ("payment_slip", "TEXT DEFAULT ''"),
    ("slip_uploaded_at", "TEXT DEFAULT ''")
]

for db in dbs:
    if not os.path.exists(db):
        print(f"Database not found: {db}")
        continue
    print(f"Migrating: {db}")
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(bookings)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    
    for col_name, col_type in new_columns:
        if col_name not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE bookings ADD COLUMN {col_name} {col_type}")
                print(f"  + Added column {col_name}")
            except Exception as e:
                print(f"  ! Error adding {col_name}: {e}")
        else:
            print(f"  = Column {col_name} already exists")
            
    conn.commit()
    conn.close()

print("Migration completed successfully.")
