import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_paths = [
    r"c:\Users\Admin\.gemini\antigravity\scratch\cat_spa\cat_spa.db",
    r"c:\Users\Admin\Downloads\cat_spa\cat_spa.db",
    r"c:\Users\Admin\Downloads\cat_spa\cat_spa\cat_spa.db",
    r"c:\Users\Admin\OneDrive\เดสก์ท็อป\cat_spa\cat_spa.db",
    r"c:\Users\Admin\OneDrive\เอกสาร\cat_spa\cat_spa.db",
    r"c:\Users\Admin\OneDrive\เอกสาร\cat_spa\cat_spa\cat_spa.db"
]

for p in db_paths:
    if os.path.exists(p):
        conn = sqlite3.connect(p)
        cur = conn.cursor()
        
        # ล้างข้อมูลการจองทั้งหมด
        cur.execute("DELETE FROM bookings")
        
        # รีเซ็ตตัวนับ AUTOINCREMENT ของตาราง bookings ให้เริ่มต้นนับ 1 ใหม่
        cur.execute("DELETE FROM sqlite_sequence WHERE name = 'bookings'")
        conn.commit()

        # ตรวจสอบตัวนับใน sqlite_sequence
        seq = cur.execute("SELECT name, seq FROM sqlite_sequence").fetchall()
        b_count = cur.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
        cats = cur.execute("SELECT cat_id, cat_name FROM cats").fetchall()
        
        print(f"Updated: {p}")
        print(f"  Bookings count: {b_count}")
        print(f"  sqlite_sequence: {seq}")
        print(f"  Cats remaining: {cats}")
        conn.close()

print("ALL_RESET_COMPLETE")
