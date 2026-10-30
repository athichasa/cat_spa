import io
import os
import sys
import sqlite3
sys.stdout.reconfigure(encoding="utf-8")

from app import app, calculate_distance_km, calculate_delivery_fee, SHOP_LAT, SHOP_LNG

def test_distance_and_fee_calculation():
    # Store at KKU Education (16.4743, 102.8225)
    # Test point 1: Complex KKU (16.4680, 102.8250) ~ 0.8 km
    dist1 = calculate_distance_km(SHOP_LAT, SHOP_LNG, 16.4680, 102.8250)
    assert 0.5 <= dist1 <= 1.5, f"Expected ~0.8 km, got {dist1}"
    
    # Within 2 km:
    fee_none = calculate_delivery_fee("none", dist1)
    assert fee_none == 0, f"Expected 0 for none, got {fee_none}"

    fee_pickup = calculate_delivery_fee("pickup_only", dist1)
    assert fee_pickup == 40, f"Expected 40 for <= 2km pickup, got {fee_pickup}"

    fee_round = calculate_delivery_fee("round_trip", dist1)
    assert fee_round == 70, f"Expected 70 for <= 2km round trip, got {fee_round}"

    # Test point 2: Central Khon Kaen (16.4328, 102.8236) ~ 4.6 km
    dist2 = calculate_distance_km(SHOP_LAT, SHOP_LNG, 16.4328, 102.8236)
    assert 4.0 <= dist2 <= 5.5, f"Expected ~4.6 km, got {dist2}"

    # Over 2 km:
    fee_pickup_far = calculate_delivery_fee("pickup_only", dist2)
    expected_far = 40 + int(round((dist2 - 2.0) * 10))
    assert fee_pickup_far == expected_far, f"Expected {expected_far}, got {fee_pickup_far}"

    # 4.6 km round trip:
    fee_round_far = calculate_delivery_fee("round_trip", dist2)
    expected_round = 70 + int(round((dist2 - 2.0) * 18))
    assert fee_round_far == expected_round, f"Expected {expected_round}, got {fee_round_far}"
    print("[PASS] Distance and fee calculation verified!")

def test_booking_and_payment_flow():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    client = app.test_client()

    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "อธิชา สถิตบรรจง"
        sess["role"] = "customer"

    from database import get_db_connection
    conn = get_db_connection()
    conn.execute("DELETE FROM bookings WHERE booking_date IN ('2026-11-25', '2026-11-26')")
    conn.commit()
    conn.close()

    # 1. Create booking with pay_at_shop & no delivery (self pickup)
    res1 = client.post("/bookings/new", data={
        "cat_id": 2,
        "package_id": "bath_short",
        "booking_date": "2026-11-25",
        "booking_time": "10:00",
        "notes": "พาแมวมาเอง ชำระหน้าร้าน",
        "delivery_type": "none",
        "payment_method": "pay_at_shop"
    }, follow_redirects=True)
    assert res1.status_code == 200, f"res1 failed with code {res1.status_code}"
    print("[PASS] Booking 1: Pay at shop created successfully")

    # 2. Create booking with QR Code & Pet Taxi pickup
    mock_slip = (io.BytesIO(b"fake_slip_image_content"), "test_slip.png")
    res2 = client.post("/bookings/new", data={
        "cat_id": 2,
        "package_id": "spa_coat",
        "booking_date": "2026-11-26",
        "booking_time": "14:00",
        "notes": "รับส่งน้องแมว จ่าย QR",
        "delivery_type": "round_trip",
        "pickup_address": "หน้า มข. คณะศึกษาศาสตร์",
        "latitude": 16.4700,
        "longitude": 102.8200,
        "delivery_notes": "โทรบอกล่วงหน้า 10 นาที",
        "payment_method": "qr_code",
        "payment_slip": mock_slip
    }, content_type="multipart/form-data", follow_redirects=True)
    assert res2.status_code == 200, f"res2 failed with code {res2.status_code}"
    print("[PASS] Booking 2: Pet Taxi + QR Code Slip created successfully")

    # 3. Check database record for booking 2
    from database import get_db_connection
    conn = get_db_connection()
    b2 = conn.execute("SELECT * FROM bookings ORDER BY booking_id DESC LIMIT 1").fetchone()
    assert b2["payment_method"] == "qr_code"
    assert b2["payment_status"] == "รอตรวจสอบสลิป"
    assert b2["payment_slip"].startswith("slip_")
    assert b2["delivery_type"] == "round_trip"
    assert b2["distance_km"] > 0
    assert b2["delivery_fee"] > 0
    booking_id = b2["booking_id"]
    slip_filename = b2["payment_slip"]
    conn.close()
    print(f"[PASS] Booking 2 DB check: id={booking_id}, slip={slip_filename}, fee={b2['delivery_fee']}")

    # 4. Customer views their slip
    res_slip = client.get(f"/uploads/slip/{slip_filename}")
    assert res_slip.status_code == 200
    assert res_slip.data == b"fake_slip_image_content"
    print("[PASS] Customer can view their uploaded slip")

    # 5. Customer views /bookings page
    res_bookings = client.get("/bookings")
    assert res_bookings.status_code == 200
    assert "รอตรวจสอบสลิป".encode("utf-8") in res_bookings.data or "สแกน QR Code".encode("utf-8") in res_bookings.data
    print("[PASS] Customer bookings list shows payment status and badge")

    # 6. Admin login & view admin bookings
    with client.session_transaction() as sess:
        sess["user_id"] = 2
        sess["user_name"] = "มะลิ"
        sess["role"] = "admin"

    res_admin = client.get("/admin/bookings")
    assert res_admin.status_code == 200
    assert slip_filename.encode("utf-8") in res_admin.data
    print("[PASS] Admin bookings page displays slip thumbnail and verification actions")

    # 7. Admin updates payment status to 'ชำระเงินแล้ว'
    res_update = client.post(f"/admin/bookings/{booking_id}/update-payment", data={
        "payment_status": "ชำระเงินแล้ว"
    }, follow_redirects=True)
    assert res_update.status_code == 200

    conn = get_db_connection()
    b_updated = conn.execute("SELECT payment_status FROM bookings WHERE booking_id = ?", (booking_id,)).fetchone()
    assert b_updated["payment_status"] == "ชำระเงินแล้ว"
    conn.close()
    print("[PASS] Admin payment status update to 'ชำระเงินแล้ว' verified successfully")

if __name__ == "__main__":
    test_distance_and_fee_calculation()
    test_booking_and_payment_flow()
    print("\nALL AUTOMATED TESTS PASSED SUCCESSFULLY! :)")
