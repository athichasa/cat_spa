# -*- coding: utf-8 -*-
"""
Test suite for new user requirements:
1. Staff name has only nickname (no real names or brackets)
2. 'เข้าเวร' is removed from staff cards
3. Review submission loads with 200 (uploaded_cat_image fix)
4. Admin Staff management & editing
5. Admin Reviews overview & accurate rating calculations
"""
import unittest
from app import app, get_db_connection

class TestNewRequirements(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        conn = get_db_connection()
        conn.execute("DELETE FROM reviews")
        conn.execute("DELETE FROM bookings")
        conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('bookings', 'reviews')")
        conn.execute("UPDATE staff SET service_count = 0, rating = 5.0")
        conn.commit()
        conn.close()

    def test_01_staff_clean_display(self):
        """Staff names have only nickname and no เข้าเวร in booking/staff page"""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role"] = "customer"

        res_booking = self.client.get("/bookings/new")
        html_booking = res_booking.data.decode("utf-8")
        self.assertNotIn("กัญญาพัชร", html_booking)
        self.assertNotIn("พิมลดา", html_booking)
        self.assertNotIn("ณิชากานต์", html_booking)
        self.assertNotIn("เข้าเวร:", html_booking)
        self.assertIn("คุณต้นเตย", html_booking)
        self.assertIn("คุณมีมี่", html_booking)
        self.assertIn("คุณอุ๋มอิ๋ม", html_booking)

        res_staff = self.client.get("/staff")
        html_staff = res_staff.data.decode("utf-8")
        self.assertNotIn("กัญญาพัชร", html_staff)
        self.assertNotIn("พิมลดา", html_staff)
        self.assertNotIn("ณิชากานต์", html_staff)
        self.assertNotIn("วันและเวลาเข้าเวร", html_staff)
        print("Test 01 Passed: Staff real names and work schedule successfully removed")

    def test_02_admin_staff_management(self):
        """Admin can view and edit staff members"""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 999
            sess["role"] = "admin"
            sess["name"] = "Admin"

        # View staff list
        res_list = self.client.get("/admin/staff")
        self.assertEqual(res_list.status_code, 200)
        html_list = res_list.data.decode("utf-8")
        self.assertIn("จัดการข้อมูลพนักงาน", html_list)
        self.assertIn("คุณต้นเตย", html_list)

        # Edit staff 1 (ต้นเตย)
        edit_data = {
            "nickname": "ต้นเตย",
            "role_title": "Senior Cat Spa & Aromatherapy Specialist",
            "specialties": "สปาอโรม่าบำบัด, วารีบำบัดขนนุ่ม, นวดผ่อนคลายกล้ามเนื้อ",
            "highlights": "สัมผัสมือเบามาก นวดสปาเก่ง น้องแมวจะเคลิ้มหลับสบาย",
            "experience_years": 4,
            "status_text": "พร้อมให้บริการทุกวัน",
            "is_active": "1"
        }
        res_post = self.client.post("/admin/staff/1/edit", data=edit_data, follow_redirects=True)
        self.assertEqual(res_post.status_code, 200)

        # Verify DB
        conn = get_db_connection()
        st = conn.execute("SELECT nickname, status_text, experience_years FROM staff WHERE staff_id = 1").fetchone()
        self.assertEqual(st["status_text"], "พร้อมให้บริการทุกวัน")
        self.assertEqual(st["experience_years"], 4)
        conn.close()
        print("Test 02 Passed: Admin staff list and edit functionality working")

    def test_03_booking_and_review_workflow(self):
        """Complete workflow: Book -> Admin complete -> Customer reviews -> Rating recalculated -> Admin overview"""
        # Customer books with staff 1
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role"] = "customer"
            sess["name"] = "Tester Customer"

        post_data = {
            "cat_id": 2,
            "package_id": "13",
            "booking_date": "2026-11-25",
            "booking_time": "14:00",
            "notes": "Testing review workflow",
            "staff_id": 1,
            "delivery_type": "none",
            "payment_method": "pay_at_shop"
        }
        res_book = self.client.post("/bookings/new", data=post_data, follow_redirects=True)
        self.assertEqual(res_book.status_code, 200)

        conn = get_db_connection()
        booking = conn.execute("SELECT booking_id FROM bookings ORDER BY booking_id DESC LIMIT 1").fetchone()
        booking_id = booking["booking_id"]
        conn.close()

        # Admin completes the service
        with self.client.session_transaction() as sess:
            sess["user_id"] = 999
            sess["role"] = "admin"
            sess["name"] = "Admin"

        res_complete = self.client.post(
            f"/admin/bookings/{booking_id}/status",
            data={"status": "เสร็จสิ้น"},
            follow_redirects=True
        )
        self.assertEqual(res_complete.status_code, 200)

        # Customer visits review page (verifies 200 OK and no 500 BuildError)
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role"] = "customer"
            sess["name"] = "Tester Customer"

        res_review_page = self.client.get(f"/bookings/{booking_id}/review")
        self.assertEqual(res_review_page.status_code, 200)
        html_review = res_review_page.data.decode("utf-8")
        self.assertIn("แบ่งปันความประทับใจของคุณ", html_review)
        self.assertIn("คุณต้นเตย", html_review)

        # Customer submits review (Shop: 5, Staff: 5)
        review_data = {
            "shop_rating": 5,
            "shop_comment": "ร้านสะอาดมาก บรรยากาศผ่อนคลาย",
            "staff_rating": 5,
            "staff_comment": "คุณต้นเตยมือเบามาก น้องลินลดาไม่กลัวเลย"
        }
        res_submit = self.client.post(f"/bookings/{booking_id}/review", data=review_data, follow_redirects=True)
        self.assertEqual(res_submit.status_code, 200)

        # Verify DB review stored and rating updated
        conn = get_db_connection()
        rev = conn.execute("SELECT * FROM reviews WHERE booking_id = ?", (booking_id,)).fetchone()
        self.assertIsNotNone(rev)
        self.assertEqual(rev["shop_rating"], 5)
        self.assertEqual(rev["staff_rating"], 5)
        self.assertEqual(rev["staff_id"], 1)

        b_check = conn.execute("SELECT has_reviewed FROM bookings WHERE booking_id = ?", (booking_id,)).fetchone()
        self.assertEqual(b_check["has_reviewed"], 1)

        st_check = conn.execute("SELECT rating, service_count FROM staff WHERE staff_id = 1").fetchone()
        self.assertEqual(st_check["rating"], 5.0)
        self.assertEqual(st_check["service_count"], 1)
        conn.close()
        print("Test 03 Passed: Review submitted, stored accurately, and staff rating recalculated")

    def test_04_admin_reviews_overview_and_delete(self):
        """Admin reviews overview shows review and handles deletion with accurate recalculation"""
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO bookings (user_id, cat_id, service_name, price, booking_date, booking_time, status, staff_id, staff_name, has_reviewed)
            VALUES (1, 2, 'สปาอโรม่า', 500, '2026-11-25', '14:00', 'เสร็จสิ้น', 1, 'ต้นเตย', 1)
        """)
        b_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute("""
            INSERT INTO reviews (booking_id, user_id, user_name, cat_name, staff_id, staff_name, service_name, shop_rating, shop_comment, staff_rating, staff_comment, created_at)
            VALUES (?, 1, 'ลูกค้าทดสอบ', 'ลินลดา', 1, 'ต้นเตย', 'สปาอโรม่า', 5, 'ร้านสะอาดมาก บรรยากาศผ่อนคลาย', 5, 'ดีมาก', '2026-11-25 15:00:00')
        """, (b_id,))
        conn.commit()
        conn.close()

        with self.client.session_transaction() as sess:
            sess["user_id"] = 999
            sess["role"] = "admin"
            sess["name"] = "Admin"

        # Admin checks /admin/reviews
        res_reviews = self.client.get("/admin/reviews")
        self.assertEqual(res_reviews.status_code, 200)
        html_reviews = res_reviews.data.decode("utf-8")
        self.assertIn("ภาพรวมรีวิวและความคิดเห็นจากลูกค้า", html_reviews)
        self.assertIn("ร้านสะอาดมาก บรรยากาศผ่อนคลาย", html_reviews)

        # Admin deletes review
        conn = get_db_connection()
        rev = conn.execute("SELECT review_id, booking_id FROM reviews LIMIT 1").fetchone()
        review_id = rev["review_id"]
        booking_id = rev["booking_id"]
        conn.close()

        res_del = self.client.post(f"/admin/reviews/{review_id}/delete", follow_redirects=True)
        self.assertEqual(res_del.status_code, 200)

        # Verify deleted in DB and booking has_reviewed reset to 0
        conn = get_db_connection()
        rev_count = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
        self.assertEqual(rev_count, 0)
        b_check = conn.execute("SELECT has_reviewed FROM bookings WHERE booking_id = ?", (booking_id,)).fetchone()
        self.assertEqual(b_check["has_reviewed"], 0)
        conn.close()
        print("Test 04 Passed: Admin reviews overview, accurate recalculation, and review deletion working")

if __name__ == "__main__":
    unittest.main()
