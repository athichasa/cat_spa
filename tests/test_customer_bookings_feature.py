import unittest
import sqlite3
import os
from app import app, init_db, get_db_connection

class TestCustomerBookingsFeature(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "test_secret"
        self.client = self.app.test_client()

        # สร้างผู้ใช้ทดสอบแยกต่างหาก user_id = 99999 (ไม่รบกวนข้อมูลจริงของลูกค้า user_id 1)
        self.test_user_id = 99999
        conn = get_db_connection()
        conn.execute("DELETE FROM bookings WHERE user_id = ?", (self.test_user_id,))
        conn.execute("DELETE FROM cats WHERE user_id = ?", (self.test_user_id,))
        conn.execute("DELETE FROM users WHERE user_id = ?", (self.test_user_id,))

        conn.execute("""
            INSERT INTO users (user_id, email, password, name, phone, role)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.test_user_id, "test_dummy_user@test.com", "testpass", "ทดสอบ ระบบ", "0899999999", "customer"))

        conn.execute(
            "INSERT INTO cats (user_id, cat_name, breed, age) VALUES (?, ?, ?, ?)",
            (self.test_user_id, "ส้มส้ม", "ไทย", 2)
        )
        conn.execute(
            "INSERT INTO cats (user_id, cat_name, breed, age) VALUES (?, ?, ?, ?)",
            (self.test_user_id, "มังคุด", "บริติช", 1)
        )
        conn.commit()

        cat1 = conn.execute("SELECT cat_id FROM cats WHERE user_id = ? AND cat_name = 'ส้มส้ม'", (self.test_user_id,)).fetchone()
        cat2 = conn.execute("SELECT cat_id FROM cats WHERE user_id = ? AND cat_name = 'มังคุด'", (self.test_user_id,)).fetchone()
        self.cat1_id = cat1["cat_id"]
        self.cat2_id = cat2["cat_id"]

        # สร้างการจอง 3 รายการสำหรับ test user เท่านั้น
        conn.execute("""
            INSERT INTO bookings (user_id, cat_id, service_name, price, booking_date, booking_time, status, payment_method, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (self.test_user_id, self.cat1_id, "อาบน้ำตัดขนพื้นฐาน", 350, "2026-10-20", "10:00", "ยืนยันแล้ว", "qr_code", "ชำระเงินแล้ว"))

        conn.execute("""
            INSERT INTO bookings (user_id, cat_id, service_name, price, booking_date, booking_time, status, payment_method, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (self.test_user_id, self.cat2_id, "อาบน้ำสปาอโรม่า", 550, "2026-10-21", "11:00", "รอยืนยัน", "pay_at_shop", "รอชำระหน้าร้าน"))

        conn.execute("""
            INSERT INTO bookings (user_id, cat_id, service_name, price, booking_date, booking_time, status, payment_method, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (self.test_user_id, self.cat1_id, "วารีบำบัด", 650, "2026-10-22", "13:00", "รอยืนยัน", "qr_code", "รอตรวจสอบสลิป"))

        conn.commit()
        conn.close()

    def tearDown(self):
        # ล้างข้อมูลของ test user เท่านั้น
        conn = get_db_connection()
        conn.execute("DELETE FROM bookings WHERE user_id = ?", (self.test_user_id,))
        conn.execute("DELETE FROM cats WHERE user_id = ?", (self.test_user_id,))
        conn.execute("DELETE FROM users WHERE user_id = ?", (self.test_user_id,))
        conn.commit()
        conn.close()

    def test_bookings_page_order_and_accordion(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = self.test_user_id
            sess["role"] = "customer"

        response = self.client.get("/bookings")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")

        # ตรวจสอบว่ามี Accordion markup
        self.assertIn("booking-summary-header", html)
        self.assertIn("queue-badge", html)
        self.assertIn("ดูรายละเอียด", html)
        self.assertIn("booking-detail-body", html)
        self.assertIn("toggleBookingCard", html)

        # ตรวจสอบปุ่ม Filter
        self.assertIn("🐾 รวมแมวทุกตัว", html)
        self.assertIn("น้องส้มส้ม", html)
        self.assertIn("น้องมังคุด", html)

        # ตรวจสอบลำดับล่าสุดก่อน (DESC): คิวที่ 3 ต้องปรากฏก่อนคิวที่ 2 และคิวที่ 1
        pos3 = html.find("วารีบำบัด")
        pos2 = html.find("อาบน้ำสปาอโรม่า")
        pos1 = html.find("อาบน้ำตัดขนพื้นฐาน")
        self.assertTrue(pos3 < pos2 < pos1, f"ลำดับต้องเป็น คิว 3 (ล่าสุด) -> คิว 2 -> คิว 1 (เก่าสุด): pos3={pos3}, pos2={pos2}, pos1={pos1}")

    def test_filter_by_cat(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = self.test_user_id
            sess["role"] = "customer"

        # กรองเฉพาะน้องมังคุด (cat2)
        response = self.client.get(f"/bookings?cat_id={self.cat2_id}")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")

        self.assertIn("น้องมังคุด", html)
        self.assertIn("อาบน้ำสปาอโรม่า", html)
        # ไม่ควรมีการจองของส้มส้มใน server-rendered html เมื่อกรอง cat2
        self.assertNotIn("วารีบำบัด", html)
        self.assertNotIn("อาบน้ำตัดขนพื้นฐาน", html)

if __name__ == "__main__":
    unittest.main()
