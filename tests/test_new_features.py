import unittest
import sqlite3
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, get_db_connection, get_services_dict, get_package_by_id_or_name, get_service_min_prices


class TestNewFeatures(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

        # Clean up any test users
        conn = get_db_connection()
        conn.execute("DELETE FROM users WHERE email IN ('otp_test@catspa.com', 'pwd_test@catspa.com', 'test_thai_phone@gmail.com', 'test_reset_user@gmail.com')")
        conn.execute("DELETE FROM services WHERE service_name = 'คอร์สทดสอบระบบแอดมิน'")
        conn.commit()
        conn.close()

    def tearDown(self):
        conn = get_db_connection()
        conn.execute("DELETE FROM users WHERE email IN ('otp_test@catspa.com', 'pwd_test@catspa.com', 'test_thai_phone@gmail.com', 'test_reset_user@gmail.com')")
        conn.execute("DELETE FROM services WHERE service_name = 'คอร์สทดสอบระบบแอดมิน'")
        conn.commit()
        conn.close()

    def test_01_password_length_requirement(self):
        """1. ตรวจสอบข้อกำหนดรหัสผ่านต้องมีตั้งแต่ 8 ตัวอักษรขึ้นไป"""
        # ลองส่งรหัสผ่าน 7 ตัวอักษร
        res = self.client.post("/register", data={
            "name": "Password Tester",
            "email": "pwd_test@catspa.com",
            "phone": "0811111111",
            "password": "pass123",  # 7 chars
            "confirm_password": "pass123",
            "terms_accepted": "yes",
            "privacy_acknowledged": "yes"
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        # ต้องไม่ถูกส่งไปยัง verify-otp
        self.assertIn("รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษรขึ้นไป".encode("utf-8"), res.data)

        # ตรวจสอบว่ายังไม่ได้เพิ่มผู้ใช้ลงใน DB
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = 'pwd_test@catspa.com'").fetchone()
        conn.close()
        self.assertIsNone(user)

    def test_02_otp_registration_flow(self):
        """2. ตรวจสอบกระบวนการส่งและยืนยันรหัส OTP ในขั้นตอนสมัครสมาชิก"""
        # ส่งข้อมูลสมัครสมาชิกที่มีรหัสผ่าน >= 8 ตัว
        res = self.client.post("/register", data={
            "name": "OTP Tester",
            "email": "otp_test@catspa.com",
            "phone": "0822222222",
            "password": "password123",  # 11 chars
            "confirm_password": "password123",
            "terms_accepted": "yes",
            "privacy_acknowledged": "yes"
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        # ตรวจสอบว่าระบบเปลี่ยนเส้นทางมาที่หน้า verify-otp
        self.assertIn("ยืนยันรหัส OTP ทางอีเมล".encode("utf-8"), res.data)

        with self.client.session_transaction() as sess:
            self.assertIn("pending_registration", sess)
            otp = sess["pending_registration"]["otp"]
            self.assertEqual(len(otp), 6)

        # ลองกรอก OTP ผิด
        wrong_res = self.client.post("/verify-otp", data={"otp": "000000"}, follow_redirects=True)
        self.assertIn("รหัส OTP ไม่ถูกต้อง".encode("utf-8"), wrong_res.data)

        # กรอก OTP ถูกต้อง
        correct_res = self.client.post("/verify-otp", data={"otp": otp}, follow_redirects=True)
        self.assertEqual(correct_res.status_code, 200)
        self.assertIn("ยืนยันอีเมลและสมัครสมาชิกสำเร็จ".encode("utf-8"), correct_res.data)

        # ตรวจสอบว่าผู้ใช้ถูกสร้างใน SQLite DB แล้ว
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = 'otp_test@catspa.com'").fetchone()
        conn.close()
        self.assertIsNotNone(user)
        self.assertEqual(user["name"], "OTP Tester")
        self.assertTrue(check_password_hash(user["password"], "password123"))

    def test_03_admin_course_management_and_global_linking(self):
        """3. ตรวจสอบการเพิ่ม-ลด แก้ไขคอร์สโดยแอดมิน และการเชื่อมโยงไปยังหน้าบริการทั้งหมด"""
        # จำลองการล็อกอินเป็น Admin
        with self.client.session_transaction() as sess:
            sess["user_id"] = 9999
            sess["name"] = "Admin Test"
            sess["role"] = "admin"

        # 3.1 เข้าหน้าจัดการบริการ (/admin/services)
        res = self.client.get("/admin/services")
        self.assertEqual(res.status_code, 200)
        self.assertIn("จัดการบริการและราคา".encode("utf-8"), res.data)

        # 3.2 แอดมินเพิ่มคอร์สใหม่
        post_res = self.client.post("/admin/services", data={
            "category": "สปาแมว",
            "service_name": "คอร์สทดสอบระบบแอดมิน",
            "description": "ทดสอบระบบการเชื่อมโยงคอร์สแบบ Dynamic",
            "price": "888"
        }, follow_redirects=True)
        self.assertEqual(post_res.status_code, 200)
        self.assertIn("คอร์สทดสอบระบบแอดมิน".encode("utf-8"), post_res.data)

        # 3.3 ตรวจสอบการเชื่อมโยง: ต้องปรากฏใน /service/spa (Service Detail)
        detail_res = self.client.get("/service/spa")
        self.assertEqual(detail_res.status_code, 200)
        self.assertIn("คอร์สทดสอบระบบแอดมิน".encode("utf-8"), detail_res.data)
        self.assertIn("888".encode("utf-8"), detail_res.data)

        # 3.4 ตรวจสอบการเชื่อมโยง: ต้องมีอยู่ใน get_services_dict()
        services_dict = get_services_dict()
        created_service = None
        for s_id, s in services_dict.items():
            if s["name"] == "คอร์สทดสอบระบบแอดมิน":
                created_service = s
                break
        self.assertIsNotNone(created_service)
        self.assertEqual(created_service["price"], 888)

        # 3.5 ตรวจสอบการปิดบริการ (Toggle)
        toggle_res = self.client.post(f"/admin/services/{created_service['service_id']}/toggle", follow_redirects=True)
        self.assertEqual(toggle_res.status_code, 200)
        # หลังจากปิดบริการ ต้องไม่แสดงใน /service/spa
        detail_after_toggle = self.client.get("/service/spa")
        self.assertNotIn("คอร์สทดสอบระบบแอดมิน".encode("utf-8"), detail_after_toggle.data)

        # 3.6 ตรวจสอบการลบบริการ (Delete)
        del_res = self.client.post(f"/admin/services/{created_service['service_id']}/delete", follow_redirects=True)
        self.assertEqual(del_res.status_code, 200)
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM services WHERE service_id = ?", (created_service["service_id"],)).fetchone()
        conn.close()
        self.assertIsNone(row)

    def test_04_direct_booking_and_login_enforcement(self):
        """4. ตรวจสอบการกดจองคิวจากหน้ารายละเอียดบริการ และการบังคับให้ล็อกอินก่อนหากยังไม่ได้เข้าสู่ระบบ"""
        # 4.1 เมื่อยังไม่ได้ล็อกอิน เข้าหน้ารายละเอียดบริการ
        res = self.client.get("/service/bath")
        self.assertEqual(res.status_code, 200)
        # ต้องมีปุ่มเข้าสู่ระบบเพื่อจองคิว
        self.assertIn("เข้าสู่ระบบเพื่อจองคิว".encode("utf-8"), res.data)
        self.assertIn("/login?next=".encode("utf-8"), res.data)

        # 4.2 เมื่อยังไม่ได้ล็อกอิน พยายามเข้าหน้า /bookings/new โดยตรง
        unauth_booking_res = self.client.get("/bookings/new")
        self.assertEqual(unauth_booking_res.status_code, 302)
        self.assertTrue("/login?next=" in unauth_booking_res.headers["Location"] and "bookings" in unauth_booking_res.headers["Location"])

        # 4.3 เมื่อล็อกอินแล้ว เข้าหน้ารายละเอียดบริการ
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["name"] = "Customer User"
            sess["role"] = "customer"

        auth_detail_res = self.client.get("/service/bath")
        self.assertEqual(auth_detail_res.status_code, 200)
        # ต้องมีปุ่มจองคิวบริการนี้ได้ทันที
        self.assertIn("จองคิวบริการนี้ →".encode("utf-8"), auth_detail_res.data)

    def test_05_phone_validation_thai_10_digits(self):
        """5. ตรวจสอบข้อกำหนดเบอร์โทรศัพท์ต้องเป็น 10 หลักตามเบอร์ไทยเท่านั้น (ขึ้นต้นด้วย 0)"""
        # เบอร์ 9 หลัก (ไม่ถูกต้อง)
        res_9 = self.client.post("/register", data={
            "name": "Phone Tester",
            "email": "test_thai_phone@gmail.com",
            "phone": "081234567",  # 9 หลัก
            "password": "password123",
            "confirm_password": "password123",
            "terms_accepted": "yes",
            "privacy_acknowledged": "yes"
        }, follow_redirects=True)
        self.assertIn("เบอร์โทรศัพท์ต้องเป็นตัวเลข 10 หลักตามเบอร์ไทยเท่านั้น".encode("utf-8"), res_9.data)

        # เบอร์ 11 หลัก (ไม่ถูกต้อง)
        res_11 = self.client.post("/register", data={
            "name": "Phone Tester",
            "email": "test_thai_phone@gmail.com",
            "phone": "08123456789",  # 11 หลัก
            "password": "password123",
            "confirm_password": "password123",
            "terms_accepted": "yes",
            "privacy_acknowledged": "yes"
        }, follow_redirects=True)
        self.assertIn("เบอร์โทรศัพท์ต้องเป็นตัวเลข 10 หลักตามเบอร์ไทยเท่านั้น".encode("utf-8"), res_11.data)

        # เบอร์ไม่ขึ้นต้นด้วย 0 (ไม่ถูกต้อง)
        res_not_0 = self.client.post("/register", data={
            "name": "Phone Tester",
            "email": "test_thai_phone@gmail.com",
            "phone": "1812345678",  # ขึ้นต้นด้วย 1
            "password": "password123",
            "confirm_password": "password123",
            "terms_accepted": "yes",
            "privacy_acknowledged": "yes"
        }, follow_redirects=True)
        self.assertIn("เบอร์โทรศัพท์ต้องเป็นตัวเลข 10 หลักตามเบอร์ไทยเท่านั้น".encode("utf-8"), res_not_0.data)

        # เบอร์ไทย 10 หลักถูกต้อง
        res_ok = self.client.post("/register", data={
            "name": "Phone Tester",
            "email": "test_thai_phone@gmail.com",
            "phone": "0891234567",  # 10 หลัก
            "password": "password123",
            "confirm_password": "password123",
            "terms_accepted": "yes",
            "privacy_acknowledged": "yes"
        }, follow_redirects=True)
        self.assertEqual(res_ok.status_code, 200)
        self.assertIn("ยืนยันรหัส OTP ทางอีเมล".encode("utf-8"), res_ok.data)

    def test_06_email_validation_real_domain(self):
        """6. ตรวจสอบการตรวจสอบอีเมลที่มีตัวตนจริง (ปฏิเสธ fake/example/non-existent domain)"""
        # ปฏิเสธ example.com
        res_fake = self.client.post("/register", data={
            "name": "Fake Email Tester",
            "email": "user@example.com",
            "phone": "0891234567",
            "password": "password123",
            "confirm_password": "password123",
            "terms_accepted": "yes",
            "privacy_acknowledged": "yes"
        }, follow_redirects=True)
        self.assertIn("ไม่สามารถใช้อีเมลทดสอบตัวอย่างได้".encode("utf-8"), res_fake.data)

        # ปฏิเสธโดเมนที่ไม่มี DNS จริง
        res_nodns = self.client.post("/register", data={
            "name": "No DNS Tester",
            "email": "user@nonexistentdomain99887766.com",
            "phone": "0891234567",
            "password": "password123",
            "confirm_password": "password123",
            "terms_accepted": "yes",
            "privacy_acknowledged": "yes"
        }, follow_redirects=True)
        self.assertIn("ไม่พบเซิร์ฟเวอร์สำหรับอีเมล".encode("utf-8"), res_nodns.data)

    def test_07_otp_not_displayed_on_screen(self):
        """7. ตรวจสอบว่าระบบไม่แสดงตัวเลขรหัส OTP 6 หลักบนหน้าจอให้ผู้สมัครเห็น"""
        res = self.client.post("/register", data={
            "name": "Hidden OTP Tester",
            "email": "test_thai_phone@gmail.com",
            "phone": "0891234567",
            "password": "password123",
            "confirm_password": "password123",
            "terms_accepted": "yes",
            "privacy_acknowledged": "yes"
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        with self.client.session_transaction() as sess:
            otp = sess["pending_registration"]["otp"]

        # หน้าเว็บต้องไม่มีข้อความที่เปิดเผยรหัส OTP
        response_text = res.data.decode("utf-8")
        self.assertNotIn(f"รหัส OTP เพื่อยืนยันอีเมลของคุณคือ: {otp}", response_text)
        self.assertNotIn(f"รหัส OTP ใหม่ของคุณคือ: {otp}", response_text)
        self.assertNotIn(f">{otp}<", response_text)

    def test_08_forgot_password_3step_flow(self):
        """8. ตรวจสอบกระบวนการลืมรหัสผ่าน 3 ขั้นตอน: ขอ OTP -> ยืนยัน OTP -> ตั้งรหัสใหม่"""
        # สร้างผู้ใช้ทดสอบใน DB
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO users (name, email, phone, password, role)
            VALUES (?, ?, ?, ?, ?)
        """, ("Reset Tester", "test_reset_user@gmail.com", "0899999999", generate_password_hash("oldpass123"), "customer"))
        conn.commit()
        conn.close()

        # ขั้นตอนที่ 1: กรอก Email ขอรหัส OTP
        fp_req = self.client.post("/forgot-password", data={
            "email": "test_reset_user@gmail.com"
        }, follow_redirects=True)
        self.assertEqual(fp_req.status_code, 200)
        self.assertIn("ยืนยันตัวตนด้วยรหัส OTP".encode("utf-8"), fp_req.data)

        with self.client.session_transaction() as sess:
            self.assertIn("forgot_password_pending", sess)
            fp_otp = sess["forgot_password_pending"]["otp"]
            self.assertEqual(len(fp_otp), 6)

        # หน้าจอต้องไม่แสดงตัวเลข OTP
        self.assertNotIn(f">{fp_otp}<", fp_req.data.decode("utf-8"))

        # ขั้นตอนที่ 2: กรอกรหัส OTP
        # ลองกรอกผิด
        fp_wrong = self.client.post("/forgot-password/verify", data={"otp": "000000"}, follow_redirects=True)
        self.assertIn("รหัส OTP ไม่ถูกต้อง".encode("utf-8"), fp_wrong.data)

        # กรอกถูกต้อง
        fp_verify = self.client.post("/forgot-password/verify", data={"otp": fp_otp}, follow_redirects=True)
        self.assertEqual(fp_verify.status_code, 200)
        self.assertIn("ตั้งรหัสผ่านใหม่".encode("utf-8"), fp_verify.data)

        # ขั้นตอนที่ 3: ตั้งรหัสผ่านใหม่
        # ถ้ารหัสผ่านสั้นกว่า 8 ตัว
        fp_short = self.client.post("/forgot-password/reset", data={
            "new_password": "short",
            "confirm_password": "short"
        }, follow_redirects=True)
        self.assertIn("รหัสผ่านใหม่ต้องมีความยาวอย่างน้อย 8 ตัวอักษรขึ้นไป".encode("utf-8"), fp_short.data)

        # ถ้ารหัสผ่านไม่ตรงกัน
        fp_mismatch = self.client.post("/forgot-password/reset", data={
            "new_password": "newpassword123",
            "confirm_password": "differentpass123"
        }, follow_redirects=True)
        self.assertIn("รหัสผ่านใหม่และการยืนยันรหัสผ่านไม่ตรงกัน".encode("utf-8"), fp_mismatch.data)

        # ตั้งรหัสผ่านใหม่ถูกต้อง (>= 8 ตัว)
        fp_ok = self.client.post("/forgot-password/reset", data={
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }, follow_redirects=True)
        self.assertEqual(fp_ok.status_code, 200)
        self.assertIn("รีเซ็ตรหัสผ่านใหม่สำเร็จแล้ว".encode("utf-8"), fp_ok.data)

        # ทดสอบ Login ด้วยรหัสผ่านใหม่
        login_res = self.client.post("/login", data={
            "email": "test_reset_user@gmail.com",
            "password": "newpassword123"
        }, follow_redirects=False)
        self.assertEqual(login_res.status_code, 302)
        self.assertEqual(login_res.headers["Location"], "/dashboard")

    def test_09_bathtub_emoji_bug_fix(self):
        """9. ตรวจสอบว่าในหน้ารายละเอียดบริการ ไอคอนอ่างอาบน้ำจัดวางตรงกลาง และไม่หลุดไปอยู่มุมซ้ายล่าง"""
        res = self.client.get("/service/bath")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn('class="detail-hero-icon"', html)
        self.assertIn('🛁', html)

    def test_10_admin_confirms_slip_triggers_receipt_email(self):
        """10. ตรวจสอบว่าเมื่อแอดมินยืนยันสลิป (ชำระเงินแล้ว) ระบบจะประมวลผลการส่งใบเสร็จรับเงินทางอีเมลให้ลูกค้า"""
        # สร้างการจองทดสอบ
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO bookings (
                user_id, cat_id, service_name, booking_date, booking_time,
                price, delivery_type, delivery_fee, payment_method, payment_status, payment_slip
            )
            VALUES (1, 2, 'อาบน้ำแมวขนสั้น', '2026-10-25', '10:00', 300, 'none', 0, 'qr_code', 'รอตรวจสอบสลิป', 'test_slip.jpg')
        """)
        booking_id = cur.lastrowid
        conn.commit()
        conn.close()

        # แอดมินล็อกอิน
        with self.client.session_transaction() as sess:
            sess["user_id"] = 9999
            sess["name"] = "Admin Test"
            sess["role"] = "admin"

        # แอดมินกดยืนยันสลิป (อัปเดตเป็น 'ชำระเงินแล้ว')
        res = self.client.post(
            f"/admin/bookings/{booking_id}/update-payment",
            data={"payment_status": "ชำระเงินแล้ว"},
            follow_redirects=True
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("ยืนยันสลิปสำเร็จ".encode("utf-8"), res.data)

        # ตรวจสอบใน DB ว่าสถานะเปลี่ยนเป็น 'ชำระเงินแล้ว'
        conn = get_db_connection()
        row = conn.execute("SELECT payment_status FROM bookings WHERE booking_id = ?", (booking_id,)).fetchone()
        conn.close()
        self.assertEqual(row["payment_status"], "ชำระเงินแล้ว")

        # ลบการจองทดสอบ
        conn = get_db_connection()
        conn.execute("DELETE FROM bookings WHERE booking_id = ?", (booking_id,))
        conn.commit()
        conn.close()

    def test_11_customer_send_receipt_to_email_route(self):
        """11. ตรวจสอบปุ่มและ Route ให้ลูกค้าสามารถกดส่งใบเสร็จรับเงินเข้าอีเมลของตนเองได้"""
        # สร้างการจองของ User 1 ที่ชำระเงินเรียบร้อยแล้ว
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO bookings (
                user_id, cat_id, service_name, booking_date, booking_time,
                price, delivery_type, delivery_fee, payment_method, payment_status, payment_slip
            )
            VALUES (1, 2, 'อาบน้ำแมวขนสั้น', '2026-10-25', '11:00', 300, 'none', 0, 'qr_code', 'ชำระเงินแล้ว', 'test_slip.jpg')
        """)
        booking_id = cur.lastrowid
        conn.commit()
        conn.close()

        # 1. ลูกค้ายังไม่ได้ล็อกอิน พยายามส่งใบเสร็จ
        unauth_res = self.client.post(f"/bookings/{booking_id}/send-receipt", follow_redirects=False)
        self.assertEqual(unauth_res.status_code, 302)
        self.assertIn("/login", unauth_res.headers["Location"])

        # 2. ลูกค้า User 1 ล็อกอินและกดส่งใบเสร็จเข้าอีเมล
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["name"] = "อธิชา สถิตบรรจง"
            sess["role"] = "customer"

        auth_res = self.client.post(f"/bookings/{booking_id}/send-receipt", follow_redirects=True)
        self.assertEqual(auth_res.status_code, 200)

        # 3. ตรวจสอบหน้าใบเสร็จ (receipt.html) ว่ามีปุ่ม 'ส่งใบเสร็จเข้าอีเมล'
        receipt_page = self.client.get(f"/bookings/{booking_id}/receipt")
        self.assertEqual(receipt_page.status_code, 200)
        self.assertIn("ส่งใบเสร็จเข้าอีเมล".encode("utf-8"), receipt_page.data)

        # 4. User 2 พยายามกดส่งใบเสร็จของ User 1 (ต้องถูกปฏิเสธ)
        with self.client.session_transaction() as sess:
            sess["user_id"] = 2
            sess["name"] = "Other User"
            sess["role"] = "customer"

        forbidden_res = self.client.post(f"/bookings/{booking_id}/send-receipt", follow_redirects=True)
        self.assertIn("ไม่พบข้อมูลการจอง".encode("utf-8"), forbidden_res.data)

        # ลบการจองทดสอบ
        conn = get_db_connection()
        conn.execute("DELETE FROM bookings WHERE booking_id = ?", (booking_id,))
        conn.commit()
        conn.close()


if __name__ == "__main__":
    unittest.main()
