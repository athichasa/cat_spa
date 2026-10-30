
import sqlite3
import shutil
from pathlib import Path

source = Path(r"D:\python\cat_spa.db")
target = Path(r"D:\python\cat_spa\cat_spa.db")
backup = Path(r"D:\python\cat_spa\cat_spa_before_merge.db")

# สำรองฐานข้อมูลเว็บไซต์ก่อนแก้ไข
if not backup.exists():
    shutil.copy2(target, backup)

src = sqlite3.connect(source)
dst = sqlite3.connect(target)

src.row_factory = sqlite3.Row
dst.row_factory = sqlite3.Row

try:
    # ตรวจสอบว่าตารางมีอยู่จริง
    source_count = src.execute(
        "SELECT COUNT(*) FROM bookings"
    ).fetchone()[0]

    if source_count == 0:
        print("ไม่พบรายการจองในฐานข้อมูลต้นทาง")
    else:
        # อ่านรายการจองจากไฟล์ต้นทาง
        rows = src.execute(
            "SELECT * FROM bookings"
        ).fetchall()

        # ตรวจสอบคอลัมน์ของทั้งสองฐานข้อมูล
        source_columns = {
            row["name"]
            for row in src.execute(
                "PRAGMA table_info(bookings)"
            ).fetchall()
        }

        target_columns = {
            row["name"]
            for row in dst.execute(
                "PRAGMA table_info(bookings)"
            ).fetchall()
        }

        columns = [
            name for name in source_columns
            if name in target_columns
        ]

        # เรียงคอลัมน์ตามลำดับจริงของตารางต้นทาง
        columns = [
            row["name"]
            for row in src.execute(
                "PRAGMA table_info(bookings)"
            ).fetchall()
            if row["name"] in target_columns
        ]

        dst.execute("BEGIN")

        for row in rows:
            data = {name: row[name] for name in columns}

            # ข้ามรายการที่มีอยู่แล้ว โดยใช้ booking_id
            exists = dst.execute(
                "SELECT 1 FROM bookings WHERE booking_id = ?",
                (data["booking_id"],)
            ).fetchone()

            if exists:
                print(
                    "ข้าม booking_id ที่มีอยู่แล้ว:",
                    data["booking_id"]
                )
                continue

            names = ", ".join(f'"{name}"' for name in columns)
            placeholders = ", ".join("?" for _ in columns)

            dst.execute(
                f"INSERT INTO bookings ({names}) "
                f"VALUES ({placeholders})",
                [data[name] for name in columns]
            )

        dst.commit()

        print("รายการจองต้นทาง:", source_count)
        print(
            "รายการจองในฐานข้อมูลเว็บไซต์:",
            dst.execute(
                "SELECT COUNT(*) FROM bookings"
            ).fetchone()[0]
        )

except Exception:
    dst.rollback()
    raise

finally:
    src.close()
    dst.close()
