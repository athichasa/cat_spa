import os
import sys
import unittest
import tempfile
import sqlite3

# Ensure we import app and database
from app import app, get_customer_notifications
import database

class TestPaymentAndNotifications(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()
        conn = database.get_db_connection()
        conn.execute("DELETE FROM bookings WHERE notes LIKE 'Test %'")
        conn.commit()
        conn.close()

    def tearDown(self):
        conn = database.get_db_connection()
        conn.execute("DELETE FROM bookings WHERE notes LIKE 'Test %'")
        conn.commit()
        conn.close()

    def test_database_has_notification_read_column(self):
        conn = database.get_db_connection()
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(bookings)").fetchall()]
        conn.close()
        self.assertIn("notification_read", cols)
        self.assertIn("payment_method", cols)
        self.assertIn("payment_status", cols)

    def test_round_trip_lock_rule(self):
        # Verify that round trip delivery type requires QR Code
        with self.client.session_transaction() as sess:
            # Login as customer user_id 1
            sess["user_id"] = 1
            sess["user_name"] = "Test Customer"
            sess["role"] = "customer"

        # Check existing cat
        conn = database.get_db_connection()
        cat = conn.execute("SELECT cat_id FROM cats WHERE user_id = 1 LIMIT 1").fetchone()
        service = conn.execute("SELECT service_id FROM services LIMIT 1").fetchone()
        conn.close()

        if not cat or not service:
            self.skipTest("Need at least 1 cat and 1 service to test booking")

        # 1. Round trip with attempt to pay at shop -> Should be forced to qr_code
        response = self.client.post("/bookings/new", data={
            "cat_id": cat["cat_id"],
            "package_id": "bath_short",
            "booking_date": "2026-12-01",
            "booking_time": "10:00",
            "notes": "Test round trip locking",
            "delivery_type": "round_trip",
            "pickup_address": "Near Khon Kaen University",
            "latitude": "16.4745",
            "longitude": "102.8234",
            "delivery_notes": "Call upon arrival",
            "payment_method": "pay_at_shop"  # Even if customer attempts pay_at_shop
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Verify in DB that payment_method is locked to qr_code
        conn = database.get_db_connection()
        latest = conn.execute("SELECT * FROM bookings WHERE notes = 'Test round trip locking' ORDER BY booking_id DESC LIMIT 1").fetchone()
        self.assertIsNotNone(latest)
        self.assertEqual(latest["delivery_type"], "round_trip")
        self.assertEqual(latest["payment_method"], "qr_code")
        self.assertEqual(latest["payment_status"], "รอแนบสลิป")
        booking_id = latest["booking_id"]
        conn.close()

        # 2. Test notification when admin rejects slip
        with self.client.session_transaction() as sess:
            sess["user_id"] = 999
            sess["user_name"] = "Admin"
            sess["role"] = "admin"

        resp_admin = self.client.post(f"/admin/bookings/{booking_id}/update-payment", data={
            "payment_status": "สลิปไม่ถูกต้อง"
        }, follow_redirects=True)
        self.assertEqual(resp_admin.status_code, 200)

        # Verify notification is generated for customer
        notifs = get_customer_notifications(1)
        notif_ids = [n["booking_id"] for n in notifs if n["payment_status"] == "สลิปไม่ถูกต้อง"]
        self.assertIn(booking_id, notif_ids)

        # 3. Customer views dashboard or bookings and sees notification
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Test Customer"
            sess["role"] = "customer"

        resp_cust = self.client.get("/dashboard")
        self.assertEqual(resp_cust.status_code, 200)
        self.assertIn("สลิปการโอนเงินไม่ถูกต้อง".encode("utf-8"), resp_cust.data)

        # 4. Test customer dismiss notification for cancelled/rejected booking
        with self.client.session_transaction() as sess:
            sess["user_id"] = 999
            sess["user_name"] = "Admin"
            sess["role"] = "admin"

        # Admin rejects booking
        resp_reject = self.client.post(f"/admin/bookings/{booking_id}/status", data={
            "status": "ปฏิเสธ"
        }, follow_redirects=True)
        self.assertEqual(resp_reject.status_code, 200)

        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Test Customer"
            sess["role"] = "customer"

        # Customer dismisses notification
        resp_dismiss = self.client.post(f"/bookings/{booking_id}/dismiss-notification", follow_redirects=True)
        self.assertEqual(resp_dismiss.status_code, 200)

        conn = database.get_db_connection()
        check_read = conn.execute("SELECT notification_read FROM bookings WHERE booking_id = ?", (booking_id,)).fetchone()
        self.assertEqual(check_read["notification_read"], 1)
        conn.close()

        # 5. Test pickup_only allowing pay_at_shop
        resp_pickup = self.client.post("/bookings/new", data={
            "cat_id": cat["cat_id"],
            "package_id": "bath_short",
            "booking_date": "2026-12-02",
            "booking_time": "14:00",
            "notes": "Test pickup only allows shop",
            "delivery_type": "pickup_only",
            "pickup_address": "Near Khon Kaen University",
            "latitude": "16.4745",
            "longitude": "102.8234",
            "delivery_notes": "One way",
            "payment_method": "pay_at_shop"
        }, follow_redirects=True)
        self.assertEqual(resp_pickup.status_code, 200)

        conn = database.get_db_connection()
        pickup_booking = conn.execute("SELECT * FROM bookings WHERE notes = 'Test pickup only allows shop' ORDER BY booking_id DESC LIMIT 1").fetchone()
        self.assertIsNotNone(pickup_booking)
        self.assertEqual(pickup_booking["delivery_type"], "pickup_only")
        self.assertEqual(pickup_booking["payment_method"], "pay_at_shop")
        self.assertEqual(pickup_booking["payment_status"], "รอชำระหน้าร้าน")

        # 6. Clean up test records
        conn.execute("DELETE FROM bookings WHERE notes IN ('Test round trip locking', 'Test pickup only allows shop')")
        conn.commit()
        conn.close()

if __name__ == "__main__":
    unittest.main()
