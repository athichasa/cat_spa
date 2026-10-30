#เพิ่มคำสั่ง import ให้ py รับไฟล์รูปภาพ

import os
import uuid
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_from_directory,
    abort,
    jsonify,
    Response


)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash


)

from database import get_db_connection, init_db
from datetime import datetime, timezone, date, timedelta
import random
import smtplib
import json
import re
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import math
from functools import wraps

app = Flask(__name__)


# =====================================
# ตรวจสอบสิทธิ์ Admin (Decorator)
# =====================================
def admin_required(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))

        if session.get("role") != "admin":
            flash("คุณไม่มีสิทธิ์เข้าถึงหน้านี้", "error")

            return redirect(url_for("dashboard"))

        return view_function(*args, **kwargs)

    return wrapper


# =========================================================================
# ข้อมูลพิกัดร้าน Cat Spa & Grooming (ใกล้คณะศึกษาศาสตร์ มหาวิทยาลัยขอนแก่น)
# และระบบคำนวณระยะทางสำหรับบริการรับ-ส่งน้องแมว (Pet Taxi)
# =========================================================================
SHOP_LAT = 16.4743
SHOP_LNG = 102.8225
SHOP_NAME = "Cat Spa & Grooming (ใกล้คณะศึกษาศาสตร์ มหาวิทยาลัยขอนแก่น)"
SHOP_ADDRESS = "ใกล้คณะศึกษาศาสตร์ มหาวิทยาลัยขอนแก่น ถ.มิตรภาพ ต.ในเมือง อ.เมือง จ.ขอนแก่น 40002"
SHOP_PROMPTPAY = "064-697-2101"  # เบอร์พร้อมเพย์รับชำระเงินของร้าน Cat Spa


# =========================================================================
# ระบบสร้าง PromptPay QR Code มาตรฐาน EMVCo พร้อมยอดเงินไดนามิก
# =========================================================================
def crc16_ccitt(data: str) -> str:
    crc = 0xFFFF

    for ch in data.encode("ascii"):
        crc ^= (ch << 8)

        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return f"{crc:04X}"


def generate_promptpay_payload(mobile: str, amount: float = None) -> str:
    clean = "".join(filter(str.isdigit, str(mobile or "")))

    if clean.startswith("0"):
        clean = "0066" + clean[1:]
    else:
        clean = "0066" + clean

    # Tag 29 - PromptPay Merchant Account Information (AID: A000000677010111)
    sub_tag_00 = "0016A000000677010111"
    sub_tag_01 = f"01{len(clean):02d}{clean}"
    tag_29_val = sub_tag_00 + sub_tag_01
    tag_29 = f"29{len(tag_29_val):02d}{tag_29_val}"

    # Tag 00: 01, Tag 01: 12 (Dynamic with amount) or 11 (Static)
    point_of_init = "12" if (amount is not None and amount > 0) else "11"
    parts = [
        "000201",
        f"0102{point_of_init}",
        tag_29,
        "5802TH",
        "5303764"
    ]

    if amount is not None and amount > 0:
        amt_str = f"{float(amount):.2f}"
        parts.append(f"54{len(amt_str):02d}{amt_str}")
    payload_without_crc = "".join(parts) + "6304"
    crc = crc16_ccitt(payload_without_crc)

    return payload_without_crc + crc


@app.route("/api/promptpay-qr")
def promptpay_qr_api():
    """
    API สร้างรูปภาพ QR Code พร้อมเพย์ตามมาตรฐาน EMVCo ของธนาคารแห่งประเทศไทย
    รองรับการระบุยอดเงินไดนามิกและเบอร์พร้อมเพย์

    """
    amount_str = request.args.get("amount", "0")

    try:
        amount = float(amount_str)
    except (ValueError, TypeError):
        amount = 0.0
    phone = request.args.get("phone", SHOP_PROMPTPAY)
    payload = generate_promptpay_payload(phone, amount)

    try:
        import qrcode
        import io
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=2
        )
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        return Response(buf.getvalue(), mimetype="image/png")
    except Exception:
        import urllib.parse
        encoded = urllib.parse.quote(payload)

        return redirect(f"https://api.qrserver.com/v1/create-qr-code/?size=260x260&data={encoded}")


def calculate_distance_km(lat1, lon1, lat2, lon2):
    """
    คำนวณระยะทางตามแนวเส้นรอบวงโลก (Haversine formula) จากพิกัดร้านไปยังบ้านลูกค้า
    หน่วยผลลัพธ์เป็นกิโลเมตร (ปัดเศษทศนิยม 1 ตำแหน่ง)

    """

    try:
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
            return 0.0

        lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
        R = 6371.0  # รัศมีโลกในหน่วยกิโลเมตร
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return round(R * c, 1)
    except Exception:
        return 0.0


def calculate_delivery_fee(delivery_type, distance_km):
    """
    คำนวณอัตราค่าเดินทางสำหรับบริการรับ-ส่งน้องแมวตามระยะทางจริงจากร้าน (ใกล้คณะศึกษาศาสตร์ มข.):
    - none: พาน้องมาเองที่ร้าน = 0 บาท
    - pickup_only / dropoff_only (เที่ยวเดียว):
        * 0 - 2.0 กม. แรก = 40 บาท (ค่าบริการเริ่มต้น)
        * เกิน 2.0 กม. คิดเพิ่มกิโลเมตรละ 10 บาท
    - round_trip (ไป-กลับ):
        * 0 - 2.0 กม. แรก = 70 บาท (ค่าบริการเริ่มต้น)
        * เกิน 2.0 กม. คิดเพิ่มกิโลเมตรละ 18 บาท

    """

    if delivery_type == "none" or not delivery_type:
        return 0

    try:
        dist = max(0.0, float(distance_km))
    except (ValueError, TypeError):
        dist = 0.0

    if delivery_type in ("pickup_only", "dropoff_only"):
        base_fee = 40

        if dist <= 2.0:
            return base_fee

        return int(round(base_fee + ((dist - 2.0) * 10)))
    elif delivery_type == "round_trip":
        base_fee = 70

        if dist <= 2.0:
            return base_fee

        return int(round(base_fee + ((dist - 2.0) * 18)))

    return 0


# ===== รายการบริการและราคา =====
# หมวดบริการ
SERVICE_CATEGORIES = {
    "bath": "อาบน้ำแมว",
    "spa": "สปาแมว",
    "haircut": "ตัดแต่งขน",
    "nails": "ตัดเล็บ"
}

# แพ็กเกจบริการและราคาจริง
BOOKING_SERVICES = {
    # ===== อาบน้ำแมว =====
    "bath_short": {
        "category": "bath",
        "name": "อาบน้ำแมวขนสั้น",
        "description": "อาบน้ำ ล้างแชมพู เช็ดตัว และเป่าขนให้แห้ง",
        "price": 300
    },
    "bath_medium": {
        "category": "bath",
        "name": "อาบน้ำแมวขนกึ่งยาว",
        "description": "อาบน้ำ ทำความสะอาด และเป่าขนพร้อมหวีสางขน",
        "price": 400
    },
    "bath_long": {
        "category": "bath",
        "name": "อาบน้ำแมวขนยาว",
        "description": "อาบน้ำ เป่าขน และหวีขนให้เรียบร้อย",
        "price": 500
    },
    "bath_detangle": {
        "category": "bath",
        "name": "อาบน้ำพร้อมหวีสางขนพันกัน",
        "description": "สำหรับแมวที่มีขนพันกันเล็กน้อย ใช้เวลาเพิ่มตามสภาพขน",
        "price": 600
    },
    # ===== สปาแมว =====
    "spa_coat": {
        "category": "spa",
        "name": "สปาบำรุงขน",
        "description": "อาบน้ำและใช้ผลิตภัณฑ์บำรุงขนสำหรับแมว",
        "price": 450
    },
    "spa_soft": {
        "category": "spa",
        "name": "สปาขนนุ่ม",
        "description": "อาบน้ำ บำรุงขน และหวีขนให้เรียบร้อย",
        "price": 550
    },
    "spa_skin": {
        "category": "spa",
        "name": "สปาดูแลผิวหนัง",
        "description": "ทำความสะอาดและเลือกผลิตภัณฑ์ดูแลผิวที่เหมาะสม",
        "price": 650
    },
    "spa_detangle": {
        "category": "spa",
        "name": "สปาบำรุงขนพร้อมหวีสาง",
        "description": "อาบน้ำ บำรุงขน เป่าขน และหวีสางขนพันกันเล็กน้อย",
        "price": 700
    },
    # ===== ตัดแต่งขน =====
    "haircut_trim": {
        "category": "haircut",
        "name": "เล็มขนเฉพาะจุด",
        "description": "เล็มขนบริเวณก้นหรือจุดที่จำเป็นตามความเหมาะสม",
        "price": 200
    },
    "haircut_basic": {
        "category": "haircut",
        "name": "ตัดแต่งทรงพื้นฐาน",
        "description": "เล็มและจัดทรงขนให้เรียบร้อย",
        "price": 400
    },
    "haircut_lion": {
        "category": "haircut",
        "name": "ตัดทรงสิงโต",
        "description": "ตัดขนลำตัวให้สั้นและคงขนบริเวณศีรษะตามรูปแบบทรง",
        "price": 600
    },
    "haircut_detail": {
        "category": "haircut",
        "name": "ตัดแต่งขนทั่วตัวแบบละเอียด",
        "description": "ตัดแต่งขนทั่วตัวและเก็บรายละเอียดตามทรงที่ตกลงกัน",
        "price": 700
    },
    # ===== ตัดเล็บ =====
    "nails_basic": {
        "category": "nails",
        "name": "ตัดเล็บอย่างเดียว",
        "description": "ตัดปลายเล็บอย่างระมัดระวัง",
        "price": 100
    },
    "nails_check": {
        "category": "nails",
        "name": "ตัดเล็บพร้อมตรวจอุ้งเท้า",
        "description": "ตัดเล็บและตรวจดูความเรียบร้อยของอุ้งเท้าเบื้องต้น",
        "price": 150
    },
    "nails_trim": {
        "category": "nails",
        "name": "ตัดเล็บพร้อมเล็มขนอุ้งเท้า",
        "description": "ตัดเล็บและเล็มขนบริเวณอุ้งเท้าตามความเหมาะสม",
        "price": 200
    }
}

# ตั้งค่าโฟลเดอร์อัปโหลดไฟล์ (น้องแมว)

UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # ไม่เกิน 5 MB


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

# ใช้สำหรับ Session
app.secret_key = "cat_spa_secret_key"

# สร้าง Database และ Table
init_db()

# =========================================================================
# ระบบยืนยันอีเมลด้วยรหัส OTP (Email OTP Verification System)
# ใช้อีเมล aber210129@gmail.com ในการส่งรหัส 6 หลักไปยังลูกค้า
# รองรับการตั้ง App Password ผ่านตัวแปรแวดล้อม หรือไฟล์ email_config.json
# =========================================================================
def get_email_credentials():
    sender = os.environ.get("GMAIL_SENDER_EMAIL", "aber210129@gmail.com").strip()
    password = os.environ.get("GMAIL_APP_PASSWORD", os.environ.get("EMAIL_PASSWORD", "")).replace(" ", "").strip()
    config_path = os.path.join(app.root_path, "email_config.json")

    if (not password or not sender) and os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                sender = cfg.get("gmail_sender", sender).strip()
                password = cfg.get("gmail_app_password", password).replace(" ", "").strip()
        except Exception:
            pass
    return sender, password


def send_otp_email(to_email, otp, purpose="register"):
    """
    ส่งรหัส OTP (6 หลัก) ไปยังอีเมลของลูกค้าผ่าน Gmail SMTP

    """
    sender_email, app_password = get_email_credentials()

    # บันทึกรหัส OTP ลงใน Log เซิร์ฟเวอร์สำหรับตรวจสอบความปลอดภัย (ไม่แสดงบนหน้าจอของผู้ใช้)
    try:
        app.logger.info("OTP GENERATED for %s (%s): %s", to_email, purpose, otp)
    except Exception:
        pass

    if not app_password:
        try:
            app.logger.warning("GMAIL_APP_PASSWORD not configured. Please set in email_config.json or environment.")
        except Exception:
            pass
        return False, "SMTP password not configured"

    try:
        subject_title = "สมัครสมาชิก" if purpose == "register" else "รีเซ็ตรหัสผ่าน"
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"รหัสยืนยัน OTP สำหรับ{subject_title} Cat Spa: {otp}"
        msg["From"] = f"Cat Spa & Grooming <{sender_email}>"
        msg["To"] = to_email
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 520px; margin: 0 auto; padding: 24px; border: 1.5px solid #f2ccd7; border-radius: 16px; background-color: #ffffff;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #d94771; margin-bottom: 6px;">🐾 Cat Spa & Grooming</h2>
                <p style="color: #7f6e76; font-size: 14px; margin: 0;">รหัสยืนยันตัวตนสำหรับ{subject_title}</p>
            </div>
            <div style="background-color: #fff0f4; border-radius: 12px; padding: 24px; text-align: center; margin-bottom: 20px;">
                <p style="color: #5a3b2c; font-size: 14px; margin-bottom: 10px;">รหัสยืนยัน OTP ของคุณคือ:</p>
                <div style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #d94771; padding: 10px; background: white; border-radius: 8px; display: inline-block; border: 1px dashed #f689ad;">
                    {otp}
                </div>
                <p style="color: #8c7870; font-size: 12px; margin-top: 12px; margin-bottom: 0;">รหัสนี้มีอายุการใช้งาน 10 นาที</p>
            </div>
            <p style="color: #666; font-size: 13px; line-height: 1.6;">
                หากคุณไม่ได้ส่งคำขอนี้บนเว็บไซต์ Cat Spa & Grooming กรุณาเพิกเฉยต่ออีเมลฉบับนี้
            </p>
            <hr style="border: none; border-top: 1px solid #f2ccd7; margin: 20px 0;">
            <p style="color: #aaa; font-size: 11px; text-align: center; margin: 0;">
                Cat Spa & Grooming • ขอนแก่น • โทร 064-697-2101
            </p>
        </div>

        """
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)

        try:
            app.logger.info("Successfully sent OTP email to %s", to_email)
        except Exception:
            pass
        return True, None
    except Exception as e:
        try:
            app.logger.error("Failed to send OTP email: %s", e)
        except Exception:
            pass
        return False, str(e)


def send_receipt_email(booking_id):
    """
    ส่งใบเสร็จรับเงิน (Official Electronic Receipt) ไปยังอีเมลของลูกค้า
    ทำงานอัตโนมัติเมื่อพนักงานตรวจสอบสลิปและกดยืนยันยอดเงินสำเร็จ
    หรือเมื่อลูกค้า/แอดมินกดปุ่มขอรับใบเสร็จทางอีเมล
    """
    connection = get_db_connection()
    booking = connection.execute("""
        SELECT b.*, c.cat_name, c.breed, c.gender, c.age, c.weight,
               u.name AS customer_name, u.phone AS customer_phone, u.email AS customer_email
        FROM bookings b
        LEFT JOIN cats c ON b.cat_id = c.cat_id
        LEFT JOIN users u ON b.user_id = u.user_id
        WHERE b.booking_id = ?
    """, (booking_id,)).fetchone()
    connection.close()

    if not booking or not booking["customer_email"]:
        return False, "ไม่พบข้อมูลการจองหรือไม่มีอีเมลลูกค้าในระบบ"

    booking = dict(booking)
    to_email = booking["customer_email"]
    sender_email, app_password = get_email_credentials()

    try:
        app.logger.info("SENDING RECEIPT EMAIL for booking #%s to %s", booking_id, to_email)
    except Exception:
        pass

    if not app_password:
        return False, "ยังไม่ได้ตั้งค่ารหัสผ่านอีเมลผู้ส่ง (GMAIL_APP_PASSWORD) ใน email_config.json"

    try:
        delivery_fee = booking["delivery_fee"] or 0
        total_price = booking["price"] or 0
        service_price = max(0, total_price - delivery_fee)
        date_str = (booking["booking_date"] or "").replace("-", "")
        receipt_no = f"REC-{date_str}-{booking['booking_id']:04d}"

        # ข้อความประเภทบริการรับส่ง
        delivery_text = "ไม่มี (พาน้องมาเองที่ร้าน)"

        if booking["delivery_type"] == "round_trip":
            dist = f" • ระยะทาง {booking['distance_km']} กม." if booking.get("distance_km") else ""
            delivery_text = f"รับและส่งกลับ (ไป-กลับ){dist}"
        elif booking["delivery_type"] == "pickup_only":
            dist = f" • ระยะทาง {booking['distance_km']} กม." if booking.get("distance_km") else ""
            delivery_text = f"รับน้องมาที่ร้าน (เที่ยวเดียว){dist}"
        elif booking["delivery_type"] == "dropoff_only":
            dist = f" • ระยะทาง {booking['distance_km']} กม." if booking.get("distance_km") else ""
            delivery_text = f"พาน้องส่งกลับบ้าน (เที่ยวเดียว){dist}"
        msg = MIMEMultipart("mixed")
        msg["Subject"] = f"🧾 ใบเสร็จรับเงิน #{receipt_no} (ยืนยันการชำระเงินแล้ว) - Cat Spa & Grooming"
        msg["From"] = f"Cat Spa & Grooming <{sender_email}>"
        msg["To"] = to_email
        alt_part = MIMEMultipart("alternative")
        msg.attach(alt_part)
        delivery_row_html = ""

        if booking["delivery_type"] and booking["delivery_type"] != "none":
            delivery_row_html = f"""
            <tr style="border-bottom: 1px solid #f1e8ec;">
                <td style="padding: 12px 14px;">
                    <strong>🚗 บริการรับ-ส่งน้องแมว (Pet Taxi)</strong>
                    <div style="font-size: 12px; color: #7f6e76; margin-top: 2px;">{delivery_text}</div>
                </td>
                <td style="padding: 12px 14px; text-align: center; color: #5a3b2c;">1</td>
                <td style="padding: 12px 14px; text-align: right; color: #5a3b2c;">{delivery_fee:,.2f} บาท</td>
            </tr>

            """
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 620px; margin: 0 auto; background: #ffffff; border: 1.5px solid #f2ccd7; border-radius: 18px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.06);">
            <!-- หัวใบเสร็จสีชมพูนุ่มนวล -->
            <div style="background: linear-gradient(135deg, #f0527d, #e83e6b); padding: 26px 20px; text-align: center; color: white;">
                <h1 style="margin: 0 0 6px 0; font-size: 24px; letter-spacing: 0.5px;">🐾 Cat Spa & Grooming</h1>
                <p style="margin: 0; font-size: 14px; opacity: 0.95;">ใบเสร็จรับเงินอิเล็กทรอนิกส์ (Electronic Official Receipt)</p>
            </div>
            <div style="padding: 24px 28px;">
                <!-- ป้ายแจ้งสถานะการยืนยันสลิป -->
                <div style="background: #f0fdf4; border: 1.5px solid #86efac; border-radius: 12px; padding: 14px 18px; margin-bottom: 22px; text-align: center;">
                    <div style="font-size: 22px; margin-bottom: 2px;">✅</div>
                    <strong style="color: #166534; font-size: 15px; display: block;">ยืนยันการชำระเงินเรียบร้อยแล้ว</strong>
                    <span style="color: #15803d; font-size: 13px;">พนักงานของร้านได้ตรวจสอบสลิปโอนเงินผ่าน QR Code เรียบร้อยแล้วค่ะ</span>
                </div>
                <!-- ข้อมูลเลขที่เอกสาร และ วันเวลา -->
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 13.5px; color: #475569;">
                    <tr>
                        <td style="padding: 4px 0;"><strong>เลขที่ใบเสร็จ:</strong> <span style="color: #e83e6b; font-weight: bold;">{receipt_no}</span></td>
                        <td style="padding: 4px 0; text-align: right;"><strong>วันที่ออกเอกสาร:</strong> {datetime.now().strftime('%d/%m/%Y')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px 0;"><strong>รหัสการจอง:</strong> #{booking['booking_id']}</td>
                        <td style="padding: 4px 0; text-align: right;"><strong>วัน-เวลานัดหมาย:</strong> {booking['booking_date']} เวลา {booking['booking_time']} น.</td>
                    </tr>
                </table>
                <hr style="border: none; border-top: 1px dashed #f2ccd7; margin: 16px 0;">
                <!-- ข้อมูลลูกค้า & น้องแมว -->
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 13.5px; color: #475569;">
                    <tr>
                        <td style="width: 50%; vertical-align: top; padding-right: 12px;">
                            <div style="color: #d94771; font-weight: bold; margin-bottom: 6px;">👤 ข้อมูลลูกค้า:</div>
                            <div>ชื่อ: <strong>{booking['customer_name']}</strong></div>
                            <div>เบอร์โทร: {booking['customer_phone'] or '-'}</div>
                            <div>อีเมล: {to_email}</div>
                        </td>
                        <td style="width: 50%; vertical-align: top; padding-left: 12px;">
                            <div style="color: #d94771; font-weight: bold; margin-bottom: 6px;">🐱 ข้อมูลน้องแมว:</div>
                            <div>ชื่อ: <strong>น้อง{booking['cat_name']}</strong></div>
                            <div>สายพันธุ์: {booking['breed'] or '-'}</div>
                            <div>เพศ: {booking['gender'] or '-'}</div>
                        </td>
                    </tr>
                </table>
                <!-- ตารางแจกแจงรายการค่าบริการ -->
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 13.5px;">
                    <thead>
                        <tr style="background: #fff0f5; color: #d94771; text-align: left;">
                            <th style="padding: 10px 14px; border-radius: 8px 0 0 8px;">รายการบริการ</th>
                            <th style="padding: 10px 14px; text-align: center; width: 60px;">จำนวน</th>
                            <th style="padding: 10px 14px; text-align: right; border-radius: 0 8px 8px 0; width: 120px;">จำนวนเงิน</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-bottom: 1px solid #f1e8ec;">
                            <td style="padding: 12px 14px;">
                                <strong>✂️ {booking['service_name']}</strong>
                                <div style="font-size: 12px; color: #7f6e76; margin-top: 2px;">{booking.get('service_description') or 'บริการดูแลความสะอาด อาบน้ำ สปาสำหรับน้องแมว'}</div>
                            </td>
                            <td style="padding: 12px 14px; text-align: center; color: #5a3b2c;">1</td>
                            <td style="padding: 12px 14px; text-align: right; color: #5a3b2c;">{service_price:,.2f} บาท</td>
                        </tr>
                        {delivery_row_html}
                    </tbody>
                </table>
                <!-- สรุปยอดรวม -->
                <div style="background: #fff8fa; border: 1px solid #fce7ef; border-radius: 12px; padding: 14px 18px; margin-bottom: 22px;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                        <tr>
                            <td style="padding: 4px 0; color: #7f6e76;">ยอดรวมค่าบริการ (Subtotal):</td>
                            <td style="padding: 4px 0; text-align: right; color: #5a3b2c;">{total_price:,.2f} บาท</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px 0; color: #7f6e76;">ส่วนลด / ภาษี:</td>
                            <td style="padding: 4px 0; text-align: right; color: #5a3b2c;">0.00 บาท</td>
                        </tr>
                        <tr style="border-top: 1.5px solid #f6ccd8; font-size: 16px; font-weight: bold;">
                            <td style="padding: 10px 0 4px; color: #d94771;">ยอดรวมสุทธิ (Grand Total):</td>
                            <td style="padding: 10px 0 4px; text-align: right; color: #d94771;">{total_price:,.2f} บาท</td>
                        </tr>
                    </table>
                </div>
                <!-- ข้อมูลร้านค้าและที่อยู่ -->
                <div style="text-align: center; font-size: 12px; color: #88727d; line-height: 1.6; border-top: 1px solid #f2ccd7; padding-top: 18px;">
                    <strong>{SHOP_NAME}</strong><br>
                    📍 {SHOP_ADDRESS}<br>
                    📞 โทรศัพท์ / พร้อมเพย์: {SHOP_PROMPTPAY}<br>
                    💖 ขอขอบคุณที่พาน้องแมวมาใช้บริการกับเราค่ะ
                </div>
            </div>
        </div>

        """
        alt_part.attach(MIMEText(html_body, "html", "utf-8"))

        # แนบไฟล์รูปสลิปการชำระเงินที่ลูกค้าอัปโหลดไว้ (ถ้ามี)
        if booking["payment_slip"]:
            slip_path = os.path.join(app.config["UPLOAD_FOLDER"], booking["payment_slip"])

            if os.path.exists(slip_path):
                try:
                    with open(slip_path, "rb") as f:
                        img_data = f.read()
                    ext = booking["payment_slip"].rsplit(".", 1)[-1].lower()
                    mime_sub = "jpeg" if ext in ("jpg", "jpeg") else ("png" if ext == "png" else "octet-stream")
                    img_part = MIMEImage(img_data, _subtype=mime_sub)
                    img_part.add_header("Content-Disposition", "attachment", filename=f"payment_slip_{booking['booking_id']}.{ext}")
                    msg.attach(img_part)
                except Exception:
                    pass

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)

        try:
            app.logger.info("Successfully sent receipt email for booking #%s to %s", booking_id, to_email)
        except Exception:
            pass
        return True, None
    except Exception as e:
        try:
            app.logger.error("Failed to send receipt email for booking #%s: %s", booking_id, e)
        except Exception:
            pass
        return False, str(e)


def validate_phone_thai(phone):
    """
    ตรวจสอบเบอร์โทรศัพท์: ต้องมีเพียง 10 หลักตามเบอร์ไทยเท่านั้น (ขึ้นต้นด้วย 0)
    """
    clean_phone = re.sub(r"[^0-9]", "", str(phone or ""))
    if not re.match(r"^0[0-9]{9}$", clean_phone):
        return False, "เบอร์โทรศัพท์ต้องเป็นตัวเลข 10 หลักตามเบอร์ไทยเท่านั้น (ขึ้นต้นด้วย 0 เช่น 08XXXXXXXX)"
    return True, clean_phone


def validate_email_real(email):
    """
    ตรวจสอบอีเมล:
    1. รูปแบบ syntax ถูกต้อง
    2. ไม่ใช่โดเมนตัวอย่าง/ปลอม เช่น example.com, test.com
    3. ตรวจสอบว่าโดเมนมีตัวตนจริงผ่าน DNS lookup (รองรับ @gmail.com, @hotmail.com, @kkumail.com ฯลฯ)
    """
    email = str(email or "").strip().lower()
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return False, "ไม่พบอีเมลที่ท่านกรอกมา กรุณากรอกอีเมลใหม่อีกครั้ง (เช่น @gmail.com, @hotmail.com, @kkumail.com)"
    domain = email.split("@")[1]
    blocked_domains = {"example.com", "test.com", "fake.com", "tempmail.com", "mailinator.com", "sample.com"}
    if domain in blocked_domains:
        return False, "ไม่พบอีเมลที่ท่านกรอกมา กรุณากรอกอีเมลใหม่อีกครั้ง (ไม่สามารถใช้อีเมลทดสอบตัวอย่างได้ เช่น @example.com)"

    # ตรวจสอบว่าโดเมนมีอยู่จริง
    try:
        socket.gethostbyname(domain)
    except Exception:
        return False, f"ไม่พบอีเมลที่ท่านกรอกมา กรุณากรอกอีเมลใหม่อีกครั้ง (ไม่พบเซิร์ฟเวอร์สำหรับอีเมล @{domain} กรุณาใช้อีเมลที่มีอยู่จริง เช่น @gmail.com, @hotmail.com หรือ @kkumail.com)"
    return True, email


# =========================================================================
# ระบบจัดการคอร์สบริการเชื่อมต่อฐานข้อมูล (Dynamic Course & Services Catalog)
# เชื่อมโยงข้อมูลบริการจากตาราง services ใน SQLite ไปยังทุกหน้า
# =========================================================================
CATEGORY_SLUG_MAP = {
    "อาบน้ำแมว": "bath",
    "สปาแมว": "spa",
    "ตัดแต่งขน": "haircut",
    "ตัดเล็บ": "nails",
    "bath": "bath",
    "spa": "spa",
    "haircut": "haircut",
    "nails": "nails",
}

CATEGORY_NAME_MAP = {
    "bath": "อาบน้ำแมว",
    "spa": "สปาแมว",
    "haircut": "ตัดแต่งขน",
    "nails": "ตัดเล็บ",
    "อาบน้ำแมว": "อาบน้ำแมว",
    "สปาแมว": "สปาแมว",
    "ตัดแต่งขน": "ตัดแต่งขน",
    "ตัดเล็บ": "ตัดเล็บ",
}


def get_services_dict():
    """
    ดึงรายการบริการทั้งหมดที่เปิดใช้งาน (is_active = 1) จากฐานข้อมูล SQLite
    สำหรับแสดงในหน้าจองคิว (new_booking)
    """
    connection = get_db_connection()
    rows = connection.execute("""
        SELECT service_id, category, service_name, description, price, is_active
        FROM services
        WHERE is_active = 1
        ORDER BY category, price ASC

    """).fetchall()
    connection.close()
    result = {}

    for r in rows:
        key = str(r["service_id"])
        cat_slug = CATEGORY_SLUG_MAP.get(r["category"], r["category"])
        result[key] = {
            "service_id": r["service_id"],
            "category": cat_slug,
            "category_name": r["category"],
            "name": r["service_name"],
            "description": r["description"] or "",
            "price": r["price"],
        }
    return result


def get_package_by_id_or_name(identifier):
    """
    ค้นหาข้อมูลแพ็กเกจจาก ID หรือชื่อบริการ หรือ fallback เข้า hardcoded list
    """

    if not identifier:
        return None
    
    identifier_str = str(identifier).strip()
    services_dict = get_services_dict()

    if identifier_str in services_dict:
        return services_dict[identifier_str]

    for p in services_dict.values():
        if p["name"] == identifier_str:
            return p

    # Fallback to BOOKING_SERVICES if legacy key like 'bath_short'
    if identifier_str in BOOKING_SERVICES:
        return BOOKING_SERVICES[identifier_str]

    # Directly check DB by service_id
    try:
        conn = get_db_connection()
        row = conn.execute(
            "SELECT service_id, category, service_name, description, price, is_active FROM services WHERE service_id = ?",
            (identifier_str,)
        ).fetchone()
        conn.close()

        if row:
            cat_slug = CATEGORY_SLUG_MAP.get(row["category"], row["category"])

            return {
                "service_id": row["service_id"],
                "category": cat_slug,
                "category_name": row["category"],
                "name": row["service_name"],
                "description": row["description"] or "",
                "price": row["price"],
            }
    except Exception:
        pass
    return None


def get_service_min_prices():
    """
    คำนวณราคาเริ่มต้นของแต่ละหมวดหมู่บริการจากฐานข้อมูล SQLite จริง
    เพื่อให้หน้าหลัก (index) และหน้าสมาชิก (dashboard) อัปเดตราคาทันทีเมื่อแอดมินแก้ไข
    """
    min_prices = {
        "bath": 300,
        "spa": 450,
        "haircut": 200,
        "nails": 100,
    }

    try:
        connection = get_db_connection()
        rows = connection.execute("""
            SELECT category, MIN(price) as min_price
            FROM services
            WHERE is_active = 1
            GROUP BY category

        """).fetchall()
        connection.close()

        for r in rows:
            cat_slug = CATEGORY_SLUG_MAP.get(r["category"])

            if cat_slug and r["min_price"] is not None:
                min_prices[cat_slug] = r["min_price"]
    except Exception:
        pass
    return min_prices


# =========================================================================
# ระบบข้อมูลพนักงานผู้ให้บริการ (Staff Management & Reviews)
# =========================================================================


def mask_customer_name(name):
    """ฟังก์ชันปกป้องสิทธิ์และข้อมูลส่วนบุคคลของลูกค้า โดยแสดงชื่อเพียงบางส่วน เช่น คุณอธิชา ส.*** หรือ คุณกาน***"""

    if not name:
        return "คุณลูกค้าผู้รักน้องแมว"

    clean = str(name).strip()

    if clean.startswith("คุณ"):
        clean = clean[3:].strip()
    parts = clean.split()

    if len(parts) >= 2:
        return f"คุณ{parts[0]} {parts[1][0]}.***"
    elif len(clean) > 3:
        return f"คุณ{clean[:3]}***"
    elif len(clean) > 1:
        return f"คุณ{clean[:1]}***"

    return f"คุณ{clean}***"


def get_staff_list():
    """ดึงรายชื่อพนักงานที่พร้อมให้บริการ พร้อมคะแนนเฉลี่ย จำนวนครั้งที่ให้บริการ และรีวิวล่าสุด"""
    connection = get_db_connection()

    try:
        staff_rows = connection.execute("""
            SELECT * FROM staff WHERE is_active = 1 ORDER BY staff_id ASC

        """).fetchall()
        staff_list = [dict(r) for r in staff_rows]

        for s in staff_list:
            # คำนวณคะแนนเฉลี่ยจากรีวิวของพนักงานท่านนี้โดยตรง (Strict 4.9 - 5.0)
            avg_res = connection.execute("""
                SELECT ROUND(AVG(staff_rating), 1)
                FROM reviews
                WHERE staff_id = ? AND staff_rating IS NOT NULL

            """, (s["staff_id"],)).fetchone()

            if avg_res and avg_res[0] is not None:
                s["rating"] = avg_res[0]

            # ดึงรีวิวล่าสุดของพนักงานคนนี้
            revs = connection.execute("""
                SELECT review_id, user_name, cat_name, staff_rating, staff_comment, created_at
                FROM reviews
                WHERE staff_id = ? AND staff_comment IS NOT NULL AND staff_comment != ''
                ORDER BY review_id DESC LIMIT 6

            """, (s["staff_id"],)).fetchall()
            s["reviews"] = []

            for rv in revs:
                rd = dict(rv)
                rd["masked_user_name"] = mask_customer_name(rd.get("user_name", ""))
                s["reviews"].append(rd)

            # นับจำนวนรีวิวทั้งหมด
            count_res = connection.execute("""
                SELECT COUNT(*) FROM reviews WHERE staff_id = ?

            """, (s["staff_id"],)).fetchone()
            s["review_count"] = count_res[0] if count_res else 0

            # แปลงรายการความเชี่ยวชาญเป็น list
            if s.get("specialties"):
                s["specialty_list"] = [sp.strip() for sp in re.split(r',\s*(?![^()]*\))', s["specialties"]) if sp.strip()]
            else:
                s["specialty_list"] = []

            if s.get("highlights"):
                s["highlights_chunks"] = s["highlights"].split()
            else:
                s["highlights_chunks"] = []
        return staff_list
    finally:
        connection.close()


def get_staff_by_id(staff_id):
    """ดึงข้อมูลพนักงานรายบุคคลจาก staff_id"""

    if not staff_id:
        return None
    connection = get_db_connection()
    try:
        row = connection.execute("""
            SELECT * FROM staff WHERE staff_id = ?
        """, (staff_id,)).fetchone()
        if not row:
            return None
        st = dict(row)
        if st.get("specialties"):
            st["specialty_list"] = [sp.strip() for sp in st["specialties"].split(",") if sp.strip()]
        else:
            st["specialty_list"] = []
        return st
    finally:
        connection.close()


# =========================================================================
# ระบบโหมดแจ้งเตือนสำหรับลูกค้า (Customer Notification System)
# แจ้งเตือนเมื่อสลิปไม่ถูกต้อง หรือการจองถูกยกเลิก/ปฏิเสธ หรือบริการเสร็จสิ้นรอการรีวิว
# =========================================================================
def get_customer_notifications(user_id):
    """
    ดึงรายการแจ้งเตือนสำหรับลูกค้า:
    1. สลิปไม่ถูกต้อง (payment_status = 'สลิปไม่ถูกต้อง' และ notification_read = 0)
    2. คิวถูกปฏิเสธหรือยกเลิก (status IN ('ปฏิเสธ', 'ยกเลิก', 'ยกเลิกแล้ว') และ notification_read = 0)
    3. บริการเสร็จสิ้นแล้วรอการรีวิว (status = 'เสร็จสิ้น' และ (has_reviewed IS NULL OR has_reviewed = 0))
    """
    connection = get_db_connection()
    rows = connection.execute("""
        SELECT b.*, c.cat_name
        FROM bookings b
        JOIN cats c ON b.cat_id = c.cat_id
        WHERE b.user_id = ?
          AND (
              (b.payment_status = 'สลิปไม่ถูกต้อง' AND (b.notification_read IS NULL OR b.notification_read = 0))
              OR (b.status IN ('ปฏิเสธ', 'ยกเลิก', 'ยกเลิกแล้ว') AND (b.notification_read IS NULL OR b.notification_read = 0))
              OR (b.status = 'เสร็จสิ้น' AND (b.has_reviewed IS NULL OR b.has_reviewed = 0))
          )
        ORDER BY b.booking_id DESC

    """, (user_id,)).fetchall()
    connection.close()
    return rows


@app.context_processor
def inject_notifications():
    if "user_id" in session and session.get("role") == "customer":
        try:
            notifs = get_customer_notifications(session["user_id"])
            urgent_notifs = [n for n in notifs if n["payment_status"] == 'สลิปไม่ถูกต้อง' or n["status"] in ['ปฏิเสธ', 'ยกเลิก', 'ยกเลิกแล้ว']]
            review_notifs = [n for n in notifs if n["status"] == 'เสร็จสิ้น' and (not n["has_reviewed"])]

            return {
                "customer_notifications": notifs,
                "unread_notifications_count": len(notifs),
                "urgent_notifications": urgent_notifs,
                "urgent_notifications_count": len(urgent_notifs),
                "review_notifications": review_notifs
            }
        except Exception:
            pass
    return {
        "customer_notifications": [],
        "unread_notifications_count": 0,
        "urgent_notifications": [],
        "urgent_notifications_count": 0,
        "review_notifications": []
    }

# =====================================
# หน้าแรก
# =====================================

@app.route("/", endpoint="home")
@app.route("/index", endpoint="index")
def home():
    min_prices = get_service_min_prices()
    connection = get_db_connection()

    try:
        # ดึงรีวิวความประทับใจลูกค้าสำหรับหน้าหลัก โดยกระจายให้ครบพนักงานทุกคน (ต้นเตย, มีมี่, อุ๋มอิ๋ม)
        staff_list_active = connection.execute("SELECT staff_id, nickname FROM staff WHERE is_active = 1 ORDER BY staff_id ASC").fetchall()
        shop_reviews = []
        reviews_by_staff = {}

        for st in staff_list_active:
            s_id = st["staff_id"]
            rows = connection.execute("""
                SELECT review_id, user_name, cat_name, staff_name, service_name,
                       shop_rating, shop_comment, staff_rating, staff_comment, created_at
                FROM reviews
                WHERE staff_id = ? AND ((shop_comment IS NOT NULL AND shop_comment != '') OR (staff_comment IS NOT NULL AND staff_comment != ''))
                ORDER BY review_id DESC
                LIMIT 3

            """, (s_id,)).fetchall()
            reviews_by_staff[s_id] = [dict(r) for r in rows]

        # สลับวนการ์ด (Interleave): ต้นเตย, มีมี่, อุ๋มอิ๋ม เพื่อให้การ์ดแสดงสลับกันอย่างเท่าเทียมและสวยงาม
        max_len = max((len(lst) for lst in reviews_by_staff.values()), default=0)

        for i in range(max_len):
            for st in staff_list_active:
                lst = reviews_by_staff.get(st["staff_id"], [])

                if i < len(lst):
                    rd = lst[i]
                    rd["masked_user_name"] = mask_customer_name(rd.get("user_name", ""))
                    shop_reviews.append(rd)

        # หากยังไม่ครบ 9 การ์ด ให้ดึงรีวิวทั่วไปมาเสริม
        if len(shop_reviews) < 9:
            existing_ids = {r["review_id"] for r in shop_reviews}
            extra_rows = connection.execute("""
                SELECT review_id, user_name, cat_name, staff_name, service_name,
                       shop_rating, shop_comment, staff_rating, staff_comment, created_at
                FROM reviews
                WHERE (shop_comment IS NOT NULL AND shop_comment != '') OR (staff_comment IS NOT NULL AND staff_comment != '')
                ORDER BY review_id DESC

            """).fetchall()

            for r in extra_rows:
                if r["review_id"] not in existing_ids:
                    rd = dict(r)
                    rd["masked_user_name"] = mask_customer_name(rd.get("user_name", ""))
                    shop_reviews.append(rd)
                    existing_ids.add(r["review_id"])

                    if len(shop_reviews) >= 9:
                        break
        avg_shop_res = connection.execute("""
            SELECT ROUND(AVG(shop_rating), 1) FROM reviews WHERE shop_rating IS NOT NULL

        """).fetchone()
        avg_shop_rating = avg_shop_res[0] if avg_shop_res and avg_shop_res[0] is not None else 5.0
        total_reviews = connection.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
    finally:
        connection.close()
    return render_template(
        "index.html",
        min_prices=min_prices,
        shop_reviews=shop_reviews,
        avg_shop_rating=avg_shop_rating,
        total_reviews=total_reviews
    )

# =====================================
# หน้า Register
# =====================================

@app.route("/register")
def register():
    email = request.args.get("email", "")

    return render_template("register.html", email=email)

# =====================================
# รับข้อมูล Register & เริ่มต้นส่ง OTP
# =====================================
@app.route("/register", methods=["POST"])
def register_post():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")
    if not name or not email or not phone or not password:
        flash("กรุณากรอกข้อมูลให้ครบถ้วนทุกช่อง")
        return redirect(url_for("register"))

    # ตรวจสอบเบอร์โทรศัพท์: 10 หลักตามเบอร์ไทยเท่านั้น (ขึ้นต้นด้วย 0)
    is_valid_phone, phone_res = validate_phone_thai(phone)
    if not is_valid_phone:
        flash(phone_res)
        return redirect(url_for("register"))
    phone = phone_res

    # ตรวจสอบอีเมล: syntax, โดเมนจริง, DNS lookup
    is_valid_email, email_res = validate_email_real(email)
    if not is_valid_email:
        flash(email_res)
        return redirect(url_for("register"))
    email = email_res

    # ข้อกำหนดเกี่ยวกับรหัสผ่าน: ต้องมีตั้งแต่ 8 ตัวอักษรขึ้นไป
    if len(password) < 8:
        flash("รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษรขึ้นไป")
        return redirect(url_for("register"))

    # ตรวจสอบ Password และ ยืนยันรหัสผ่าน
    if password != confirm_password:
        flash("รหัสผ่านและยืนยันรหัสผ่านไม่ตรงกัน")
        return redirect(url_for("register"))

    # เข้ารหัส Password
    hashed_password = generate_password_hash(password)

    # เชื่อมต่อ SQLite ตรวจสอบ Email ซ้ำ
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT user_id FROM users WHERE email = ?",
        (email,)
    )
    existing_user = cursor.fetchone()
    connection.close()

    if existing_user:
        flash("อีเมลนี้ถูกใช้งานแล้ว ไม่สามารถนำมาสมัครซ้ำได้ กรุณาใช้อีเมลอื่น หรือเข้าสู่ระบบ")

        return redirect(url_for("register"))

    if request.form.get("terms_accepted") != "yes":
        flash("กรุณายอมรับข้อกำหนดการใช้บริการ")

        return redirect(url_for("register"))

    if request.form.get("privacy_acknowledged") != "yes":
        flash("กรุณาอ่านและรับทราบนโยบายความเป็นส่วนตัว")

        return redirect(url_for("register"))

    consent_time = datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    )
    terms_version = "1.0"
    privacy_version = "1.0"

    # สร้างรหัส OTP 6 หลัก และกำหนดเวลาหมดอายุ 10 นาที
    otp = f"{random.randint(100000, 999999)}"
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
    session["pending_registration"] = {
        "name": name,
        "email": email,
        "phone": phone,
        "password": hashed_password,
        "consent_time": consent_time,
        "terms_version": terms_version,
        "privacy_version": privacy_version,
        "otp": otp,
        "expires_at": expires_at
    }

    # ส่งรหัส OTP ไปยังอีเมลของลูกค้า (ไม่แสดงรหัส OTP บนหน้าจอตามความต้องการของผู้ใช้)
    sent_success, err = send_otp_email(email, otp, purpose="register")

    if sent_success:
        flash(f"ระบบได้ส่งรหัสยืนยัน OTP (6 หลัก) ไปยังอีเมล {email} แล้ว กรุณาตรวจสอบในกล่องข้อความหรือโฟลเดอร์จดหมายขยะ (Spam)", "success")
    else:
        sender_email, app_pwd = get_email_credentials()

        if not app_pwd:
            flash(f"⚠️ ระบบยังไม่ได้เชื่อมต่อรหัสผ่านของอีเมล {sender_email} ใน email_config.json จึงยังไม่สามารถส่งอีเมลไปยัง {email} ได้จริง", "warning")
        else:
            flash(f"⚠️ ไม่สามารถส่งอีเมลไปยัง {email} ได้: {err}", "error")
    return redirect(url_for("verify_otp"))

# =====================================
# ยืนยันรหัส OTP (Email OTP Verification)
# =====================================
@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    pending = session.get("pending_registration")

    if not pending:
        flash("ไม่มีรายการสมัครสมาชิกที่รอยืนยัน กรุณากรอกข้อมูลใหม่อีกครั้ง")
        return redirect(url_for("register"))

    if request.method == "POST":
        input_otp = request.form.get("otp", "").strip()

        if not input_otp:
            flash("กรุณากรอกรหัส OTP 6 หลัก")
            return redirect(url_for("verify_otp"))

        # ตรวจสอบเวลาหมดอายุของ OTP
        try:
            expires_at = datetime.fromisoformat(pending["expires_at"])

            if datetime.now(timezone.utc) > expires_at:
                flash("รหัส OTP หมดอายุแล้ว กรุณากดขอรหัสใหม่")
                return redirect(url_for("verify_otp"))
        except Exception:
            pass

        # ตรวจสอบความถูกต้องของ OTP
        if input_otp != pending.get("otp"):
            flash("รหัส OTP ไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")
            return redirect(url_for("verify_otp"))

        # บันทึกข้อมูลสมาชิกลงฐานข้อมูล SQLite
        connection = get_db_connection()
        cursor = connection.cursor()

        # ตรวจสอบ email ซ้ำอีกครั้ง
        cursor.execute("SELECT user_id FROM users WHERE email = ?", (pending["email"],))

        if cursor.fetchone():
            connection.close()
            session.pop("pending_registration", None)
            flash("Email นี้ถูกใช้งานแล้ว กรุณาเข้าสู่ระบบ")

            return redirect(url_for("login"))

        cursor.execute("""
            INSERT INTO users (
                name,
                email,
                phone,
                password,
                role,
                terms_accepted_at,
                terms_version,
                privacy_acknowledged_at,
                privacy_version
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (
            pending["name"],
            pending["email"],
            pending["phone"],
            pending["password"],
            "customer",
            pending["consent_time"],
            pending["terms_version"],
            pending["consent_time"],
            pending["privacy_version"]
        ))
        connection.commit()
        connection.close()

        # เคลียร์ session ข้อมูลรอยืนยัน
        session.pop("pending_registration", None)
        flash("ยืนยันอีเมลและสมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ")
        return redirect(url_for("login"))

    # Mask email สำหรับแสดงผล เช่น a***9@gmail.com
    email = pending.get("email", "")
    masked_email = email
    if "@" in email:
        local, domain = email.split("@", 1)

        if len(local) > 2:
            masked_email = f"{local[0]}{'*' * (len(local) - 2)}{local[-1]}@{domain}"
        else:
            masked_email = f"{local[0]}*@{domain}"
    return render_template("verify_otp.html", email=email, masked_email=masked_email)

# =====================================
# ขอรหัส OTP ใหม่ (Resend OTP)
# =====================================

@app.route("/resend-otp", methods=["POST"])
def resend_otp():
    pending = session.get("pending_registration")
    if not pending:
        flash("ไม่มีรายการสมัครสมาชิกที่รอยืนยัน กรุณาสมัครสมาชิกใหม่")
        return redirect(url_for("register"))
    new_otp = f"{random.randint(100000, 999999)}"
    pending["otp"] = new_otp
    pending["expires_at"] = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
    session["pending_registration"] = pending
    sent_success, err = send_otp_email(pending["email"], new_otp, purpose="register")
    if sent_success:
        flash(f"ระบบได้ส่งรหัส OTP ใหม่ไปยังอีเมล {pending['email']} แล้ว กรุณาตรวจสอบในกล่องข้อความหรือโฟลเดอร์สแปม", "success")
    else:
        sender_email, app_pwd = get_email_credentials()

        if not app_pwd:
            flash(f"⚠️ ระบบยังไม่ได้เชื่อมต่อรหัสผ่านของอีเมล {sender_email} ใน email_config.json จึงยังไม่สามารถส่งอีเมลไปยัง {pending['email']} ได้จริง", "warning")
        else:
            flash(f"⚠️ ไม่สามารถส่งอีเมลไปยัง {pending['email']} ได้: {err}", "error")
    return redirect(url_for("verify_otp"))

# =====================================
# หน้า Login
# =====================================
@app.route("/login")
def login():
    email = request.args.get("email", "")

    return render_template("login.html", email=email)

# =====================================
# ตรวจสอบ Login
# =====================================
@app.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    next_url = request.form.get("next") or request.args.get("next") or ""
    if not email or not password:
        flash("กรุณากรอก Email และ Password ให้ครบถ้วน")
        return redirect(url_for("login", email=email, next=next_url if next_url else None))

    # เชื่อมต่อ SQLite
    connection = get_db_connection()
    cursor = connection.cursor()

    # ค้นหา User จาก Email (case-insensitive)
    cursor.execute(
        "SELECT * FROM users WHERE LOWER(email) = LOWER(?)",
        (email,)
    )
    user = cursor.fetchone()
    connection.close()

    # 1. หากไม่พบบัญชีนี้ในระบบ
    if not user:
        flash("ไม่พบบัญชีนี้ กรุณาสมัครสมาชิก")
        return redirect(url_for("login", email=email, next=next_url if next_url else None))

    # 2. หากพบอีเมล แต่รหัสผ่านไม่ถูกต้อง
    if not check_password_hash(user["password"], password):
        flash("Email หรือ Password ไม่ถูกต้อง")
        return redirect(url_for("login", email=email, next=next_url if next_url else None))

    # 3. Login สำเร็จ - สร้าง Session
    session["user_id"] = user["user_id"]
    session["name"] = user["name"]
    session["role"] = user["role"]

    try:
        app.logger.info("LOGIN SUCCESS: %s (role: %s)", user["email"], user["role"])
    except Exception:
        pass

    if user["role"] == "admin":
        return redirect(url_for("admin_dashboard"))
    elif next_url and next_url.startswith("/") and not next_url.startswith("//"):
        return redirect(next_url)
    else:
        return redirect(url_for("dashboard"))


# =========================================================================
# ลืมรหัสผ่านแบบยืนยันตัวตนด้วย OTP ทางอีเมล (3-Step Forgot Password Flow)
# ขั้นตอนที่ 1: กรอก Email เพื่อรับรหัส OTP 6 หลัก
# ขั้นตอนที่ 2: ยืนยันรหัส OTP จากอีเมล
# ขั้นตอนที่ 3: กำหนดรหัสผ่านใหม่ (อย่างน้อย 8 ตัวอักษร) พร้อมปุ่มเปิด/ปิดดูรหัส
# =========================================================================


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if not email:
            flash("กรุณากรอก Email ที่ลงทะเบียนไว้")
            return redirect(url_for("forgot_password"))
        connection = get_db_connection()
        user = connection.execute(
            "SELECT * FROM users WHERE LOWER(TRIM(email)) = ?", (email,)
        ).fetchone()
        connection.close()

        if user is None:
            flash("ไม่พบบัญชีผู้ใช้ที่ใช้อีเมลนี้ในระบบ กรุณาตรวจสอบอีเมลอีกครั้ง")
            return redirect(url_for("forgot_password"))

        # สร้างรหัส OTP 6 หลัก กำหนดหมดอายุใน 10 นาที
        otp = f"{random.randint(100000, 999999)}"
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
        session["forgot_password_pending"] = {
            "user_id": user["user_id"],
            "email": user["email"],
            "name": user["name"],
            "otp": otp,
            "expires_at": expires_at,
            "verified": False,
        }

        # ส่งรหัส OTP ไปยังอีเมล
        sent_success, err = send_otp_email(user["email"], otp, purpose="forgot_password")
        if sent_success:
            flash(f"ระบบได้ส่งรหัสยืนยัน OTP (6 หลัก) ไปยังอีเมล {user['email']} แล้ว กรุณาตรวจสอบในกล่องข้อความหรือโฟลเดอร์จดหมายขยะ (Spam)", "success")
        else:
            sender_email, app_pwd = get_email_credentials()

            if not app_pwd:
                flash(f"⚠️ ระบบยังไม่ได้เชื่อมต่อรหัสผ่านของอีเมล {sender_email} ใน email_config.json จึงยังไม่สามารถส่งอีเมลไปยัง {user['email']} ได้จริง", "warning")
            else:
                flash(f"⚠️ ไม่สามารถส่งอีเมลไปยัง {user['email']} ได้: {err}", "error")
        return redirect(url_for("forgot_password_verify"))
    return render_template("forgot_password.html")


@app.route("/forgot-password/verify", methods=["GET", "POST"])
def forgot_password_verify():
    pending = session.get("forgot_password_pending")
    if not pending:
        flash("กรุณากรอก Email เพื่อขอรหัสยืนยันก่อน")
        return redirect(url_for("forgot_password"))
    if request.method == "POST":
        input_otp = request.form.get("otp", "").strip()
        if not input_otp:
            flash("กรุณากรอกรหัส OTP 6 หลัก")

            return redirect(url_for("forgot_password_verify"))

        # ตรวจสอบเวลาหมดอายุ
        try:
            expires_at = datetime.fromisoformat(pending["expires_at"])
            if datetime.now(timezone.utc) > expires_at:
                flash("รหัส OTP หมดอายุแล้ว กรุณากดขอรหัสใหม่")
                return redirect(url_for("forgot_password_verify"))
        except Exception:
            pass

        # ตรวจสอบความถูกต้องของ OTP
        if input_otp != pending.get("otp"):
            flash("รหัส OTP ไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")
            return redirect(url_for("forgot_password_verify"))

        # ยืนยันสำเร็จ อนุญาตให้เข้าสู่หน้าตั้งรหัสผ่านใหม่
        pending["verified"] = True
        session["forgot_password_pending"] = pending
        session.modified = True
        flash("ยืนยันรหัส OTP ถูกต้องแล้ว กรุณากำหนดรหัสผ่านใหม่", "success")
        return redirect(url_for("forgot_password_reset"))

    # Mask email เช่น a***9@gmail.com
    email = pending.get("email", "")
    masked_email = email

    if "@" in email:
        local, domain = email.split("@", 1)
        if len(local) > 2:
            masked_email = f"{local[0]}{'*' * (len(local) - 2)}{local[-1]}@{domain}"
        else:
            masked_email = f"{local[0]}*@{domain}"
    return render_template("forgot_password_verify.html", email=email, masked_email=masked_email)


@app.route("/forgot-password/resend-otp", methods=["POST"])
def forgot_password_resend_otp():
    pending = session.get("forgot_password_pending")
    if not pending:
        flash("กรุณากรอก Email เพื่อขอรหัสยืนยันก่อน")

        return redirect(url_for("forgot_password"))

    new_otp = f"{random.randint(100000, 999999)}"
    pending["otp"] = new_otp
    pending["expires_at"] = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
    session["forgot_password_pending"] = pending
    sent_success, err = send_otp_email(pending["email"], new_otp, purpose="forgot_password")

    if sent_success:
        flash(f"ระบบได้ส่งรหัส OTP ใหม่ไปยังอีเมล {pending['email']} แล้ว กรุณาตรวจสอบในกล่องข้อความหรือโฟลเดอร์สแปม", "success")
    else:
        sender_email, app_pwd = get_email_credentials()
        if not app_pwd:
            flash(f"⚠️ ระบบยังไม่ได้เชื่อมต่อรหัสผ่านของอีเมล {sender_email} ใน email_config.json จึงยังไม่สามารถส่งอีเมลไปยัง {pending['email']} ได้จริง", "warning")
        else:
            flash(f"⚠️ ไม่สามารถส่งอีเมลไปยัง {pending['email']} ได้: {err}", "error")
    return redirect(url_for("forgot_password_verify"))


@app.route("/forgot-password/reset", methods=["GET", "POST"])
def forgot_password_reset():
    pending = session.get("forgot_password_pending")

    if not pending or not pending.get("verified"):
        flash("กรุณายืนยันรหัส OTP จากอีเมลก่อนตั้งรหัสผ่านใหม่")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not new_password or not confirm_password:
            flash("กรุณากรอกรหัสผ่านใหม่ให้ครบถ้วน")
            return redirect(url_for("forgot_password_reset"))

        if len(new_password) < 8:
            flash("รหัสผ่านใหม่ต้องมีความยาวอย่างน้อย 8 ตัวอักษรขึ้นไป")
            return redirect(url_for("forgot_password_reset"))

        if new_password != confirm_password:
            flash("รหัสผ่านใหม่และการยืนยันรหัสผ่านไม่ตรงกัน")
            return redirect(url_for("forgot_password_reset"))

        hashed = generate_password_hash(new_password)
        connection = get_db_connection()
        connection.execute(
            "UPDATE users SET password = ? WHERE user_id = ?",
            (hashed, pending["user_id"])
        )
        connection.commit()
        connection.close()
        session.pop("forgot_password_pending", None)
        flash("รีเซ็ตรหัสผ่านใหม่สำเร็จแล้ว สามารถเข้าสู่ระบบด้วยรหัสผ่านใหม่ได้ทันที", "success")
        return redirect(url_for("login"))

    return render_template("forgot_password_reset.html", email=pending.get("email", ""))

# =====================================
# Dashboard
# =====================================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    # แยกหน้าแอดมินออกจากหน้าลูกค้าเหมือนเดิม
    if session.get("role") == "admin":
        return redirect(url_for("admin_dashboard"))
    connection = get_db_connection()

    try:
        # 1. ดึงข้อมูลแมวของลูกค้าที่เข้าสู่ระบบเท่านั้น
        cats = connection.execute("""
            SELECT cat_id, cat_name, breed, age, image
            FROM cats
            WHERE user_id = ?
            ORDER BY cat_id DESC

        """, (session["user_id"],)).fetchall()

        # 2. ดึงประวัติการจองของลูกค้าคนนี้ พร้อมชื่อน้องแมว
        bookings = connection.execute("""
            SELECT
                b.booking_id,
                b.cat_id,
                c.cat_name,
                b.service_name,
                b.price,
                b.booking_date,
                b.booking_time,
                b.status,
                b.staff_id,
                b.staff_name,
                b.has_reviewed
            FROM bookings b
            LEFT JOIN cats c ON b.cat_id = c.cat_id
            WHERE b.user_id = ?
            ORDER BY b.booking_date DESC, b.booking_time DESC

        """, (session["user_id"],)).fetchall()
    finally:
        connection.close()

    # สรุปจำนวนการจอง
    total_bookings = len(bookings)
    pending_count = sum(
        1 for b in bookings if b["status"] == "รอยืนยัน"
    )
    confirmed_count = sum(
        1 for b in bookings if b["status"] == "ยืนยันแล้ว"
    )
    completed_count = sum(
        1 for b in bookings if b["status"] == "เสร็จสิ้น"
    )

    # นัดหมายครั้งถัดไป: วันนี้หรือวันข้างหน้า
    today = datetime.now().strftime("%Y-%m-%d")
    upcoming_bookings = [
        b for b in bookings
        if b["booking_date"] >= today
        and b["status"] == "ยืนยันแล้ว"
    ]

    # เรียงนัดหมายจากวันและเวลาใกล้ที่สุด
    upcoming_bookings.sort(
        key=lambda b: (b["booking_date"], b["booking_time"])
    )
    next_booking = (
        upcoming_bookings[0] if upcoming_bookings else None
    )

    # คำนวณราคาเริ่มต้นของบริการแบบ Dynamic จาก SQLite
    min_prices = get_service_min_prices()
    popular_services = list(BOOKING_SERVICES.items())[:4]

    # รายการบริการที่เสร็จสิ้นแต่ลูกค้ารอยังไม่ได้รีวิว
    pending_reviews = [
        b for b in bookings

        if b["status"] == "เสร็จสิ้น" and not b["has_reviewed"]
    ]

    return render_template(
        "dashboard.html",
        name=session.get("name", "ลูกค้า"),
        cats=cats,
        bookings=bookings,
        pending_reviews=pending_reviews,
        total_bookings=total_bookings,
        pending_count=pending_count,
        confirmed_count=confirmed_count,
        completed_count=completed_count,
        next_booking=next_booking,
        popular_services=popular_services,
        min_prices=min_prices
    )

# =====================================
# Logout
# =====================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# =====================================
# Run Application
# =====================================


@app.route("/my-cats")
def my_cats():
    if "user_id" not in session:
        return redirect(url_for("login"))
    connection = get_db_connection()
    cats = connection.execute(
        """
        SELECT *
        FROM cats
        WHERE user_id = ?
        ORDER BY cat_id DESC

        """,
        (session["user_id"],)
    ).fetchall()
    connection.close()
    return render_template("my_cats.html", cats=cats)


@app.route("/add-cat", methods=["GET", "POST"])
def add_cat():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        cat_name = request.form.get("cat_name", "").strip()
        breed = request.form.get("breed", "").strip()
        coat_type = request.form.get("coat_type", "")
        gender = request.form.get("gender", "")
        age = request.form.get("age") or None
        weight = request.form.get("weight") or None
        notes = request.form.get("notes", "").strip()
        image_file = request.files.get("image")
        image_filename = None

        if not cat_name:
            return "กรุณากรอกชื่อแมว", 400

        if image_file and image_file.filename:
            # ตรวจสอบว่าเป็นไฟล์รูปภาพที่รองรับ
            if not allowed_file(image_file.filename):
                return "รองรับเฉพาะไฟล์ JPG, JPEG, PNG และ WEBP", 400
            extension = image_file.filename.rsplit(".", 1)[-1].lower()

            # สร้างชื่อไฟล์ใหม่ไม่ให้ซ้ำกัน
            image_filename = f"{uuid.uuid4().hex}.{extension}"

            # สร้างตำแหน่งจัดเก็บรูปภาพ
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            image_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                image_filename
            )

            # บันทึกรูปภาพ
            image_file.save(image_path)
        connection = get_db_connection()

        try:
            connection.execute(
                """
                INSERT INTO cats
                (user_id, cat_name, breed, coat_type, gender,
                 age, weight, notes, image)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    cat_name,
                    breed,
                    coat_type,
                    gender,
                    age,
                    weight,
                    notes,
                    image_filename
                )
            )
            connection.commit()
        except Exception:
            # ลบไฟล์หากบันทึกข้อมูลลงฐานข้อมูลไม่สำเร็จ
            if image_filename:
                image_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    image_filename
                )

                if os.path.exists(image_path):
                    os.remove(image_path)
            raise
        finally:
            connection.close()
        return redirect(url_for("my_cats"))

    return render_template("add_cat.html")


@app.route("/edit-cat/<int:cat_id>", methods=["GET", "POST"])
def edit_cat(cat_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    connection = get_db_connection()
    cat = connection.execute(
        """
        SELECT *
        FROM cats
        WHERE cat_id = ? AND user_id = ?
        """,
        (cat_id, session["user_id"])
    ).fetchone()

    if cat is None:
        connection.close()
        return "ไม่พบข้อมูลแมว หรือคุณไม่มีสิทธิ์แก้ไขข้อมูลนี้"

    if request.method == "POST":
        cat_name = request.form.get("cat_name", "").strip()
        breed = request.form.get("breed", "").strip()
        coat_type = request.form.get("coat_type", cat["coat_type"] or "")
        gender = request.form.get("gender", "")
        age = request.form.get("age") or None
        weight = request.form.get("weight") or None
        notes = request.form.get("notes", "").strip()
        image_file = request.files.get("image")
        image_filename = cat["image"]

        if image_file and image_file.filename:
            if allowed_file(image_file.filename):
                extension = image_file.filename.rsplit(".", 1)[-1].lower()
                image_filename = f"{uuid.uuid4().hex}.{extension}"
                image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
                image_file.save(image_path)
        connection.execute(
            """
            UPDATE cats
            SET cat_name = ?,
                breed = ?,
                coat_type = ?,
                gender = ?,
                age = ?,
                weight = ?,
                notes = ?,
                image = ?
            WHERE cat_id = ? AND user_id = ?
            """,
            (
                cat_name,
                breed,
                coat_type,
                gender,
                age,
                weight,
                notes,
                image_filename,
                cat_id,
                session["user_id"]
            )
        )
        connection.commit()
        connection.close()

        return redirect(url_for("my_cats"))

    connection.close()

    return render_template("edit_cat.html", cat=cat)


@app.route("/delete-cat/<int:cat_id>", methods=["POST"])
def delete_cat(cat_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    connection.execute(
        """
        DELETE FROM cats
        WHERE cat_id = ? AND user_id = ?

        """,
        (cat_id, session["user_id"])
    )
    connection.commit()
    connection.close()

    return redirect(url_for("my_cats"))

#Route สำหรับอัปโหลดรูปแมว


@app.route("/uploads/<filename>")
def uploaded_cat_image(filename):
    # อนุญาตเฉพาะผู้ใช้ที่เข้าสู่ระบบแล้ว
    if "user_id" not in session:
        return redirect(url_for("login"))

    # แอดมินสามารถดูรูปภาพน้องแมวของลูกค้าได้ทุกตัว
    if session.get("role") == "admin":
        return send_from_directory(
            app.config["UPLOAD_FOLDER"],
            filename
        )

    # ตรวจว่าไฟล์นี้เป็นรูปของแมวที่ผู้ใช้มีสิทธิ์ดู
    connection = get_db_connection()
    cat = connection.execute(
        """
        SELECT cat_id
        FROM cats
        WHERE image = ? AND user_id = ?

        """,
        (filename, session["user_id"])
    ).fetchone()
    connection.close()

    if cat is None:
        abort(404)
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


@app.route("/bookings")
def bookings():
    if "user_id" not in session:
        return redirect(url_for("login"))

    cat_id_filter = request.args.get("cat_id", "all").strip()
    connection = get_db_connection()

    # ดึงรายชื่อน้องแมวของลูกค้าคนนี้เพื่อใช้แสดงปุ่มเลือกกรอง
    cats = connection.execute("""
        SELECT cat_id, cat_name, image
        FROM cats
        WHERE user_id = ?
        ORDER BY cat_name ASC

    """, (session["user_id"],)).fetchall()

    # นับจำนวนการจองของแมวแต่ละตัวเพื่อแสดงตัวเลขบนปุ่ม
    all_user_bookings = connection.execute("""
        SELECT cat_id, COUNT(*) as count
        FROM bookings
        WHERE user_id = ?
        GROUP BY cat_id

    """, (session["user_id"],)).fetchall()
    cat_counts = {row["cat_id"]: row["count"] for row in all_user_bookings}
    total_bookings_count = sum(cat_counts.values())
    query = """
        SELECT
            bookings.*,
            cats.cat_name,
            cats.image AS cat_image
        FROM bookings
        JOIN cats ON bookings.cat_id = cats.cat_id
        WHERE bookings.user_id = ?
    """

    params = [session["user_id"]]
    if cat_id_filter and cat_id_filter != "all":
        try:
            cid = int(cat_id_filter)
            query += " AND bookings.cat_id = ?"
            params.append(cid)
        except ValueError:
            cat_id_filter = "all"

    # เรียงจากการจองครั้งล่าสุดเรียงลงไปถึงครั้งแรก (Latest booking first)
    query += " ORDER BY bookings.booking_id DESC"
    my_bookings = connection.execute(query, params).fetchall()
    connection.close()
    pending_reviews = [
        b for b in my_bookings
        if b["status"] == "เสร็จสิ้น" and not b["has_reviewed"]
    ]

    return render_template(
        "bookings.html",
        bookings=my_bookings,
        pending_reviews=pending_reviews,
        cats=cats,
        selected_cat_id=cat_id_filter,
        cat_counts=cat_counts,
        total_bookings_count=total_bookings_count
    )


@app.route("/bookings/new", methods=["GET", "POST"])
def new_booking():
    if "user_id" not in session:
        flash("กรุณาเข้าสู่ระบบก่อนทำการจองคิวบริการ", "info")
        target_next = request.full_path if request.query_string else request.path
        return redirect(url_for("login", next=target_next))

    # เวลาที่ร้านเปิดให้เลือกจอง
    time_slots = [
        "09:00", "10:00", "11:00",
        "13:00", "14:00", "15:00",
        "16:00", "17:00", "18:00", "19:00"
    ]
    services = get_services_dict()
    connection = get_db_connection()
    cats = connection.execute("""
        SELECT cat_id, cat_name
        FROM cats
        WHERE user_id = ?
        ORDER BY cat_name

    """, (session["user_id"],)).fetchall()

    if request.method == "POST":
        cat_id = request.form.get("cat_id", type=int)
        package_id = request.form.get("package_id")
        booking_date = request.form.get("booking_date", "")
        booking_time = request.form.get("booking_time", "")
        notes = request.form.get("notes", "").strip()
        package = get_package_by_id_or_name(package_id)

        # 1. ตรวจสอบว่ากรอกข้อมูลครบ
        if not cat_id or not package:
            connection.close()
            return "กรุณาเลือกน้องแมวและแพ็กเกจ", 400

        if not booking_date or not booking_time:
            connection.close()
            return "กรุณาเลือกวันที่และเวลา", 400

        # 2. ตรวจสอบรูปแบบวันที่และเวลา
        try:
            selected_date = datetime.strptime(
                booking_date, "%Y-%m-%d"
            ).date()
            selected_time = datetime.strptime(
                booking_time, "%H:%M"
            ).time()
        except ValueError:
            connection.close()
            return "รูปแบบวันที่หรือเวลาไม่ถูกต้อง", 400

        # 3. ห้ามเลือกวันที่ย้อนหลัง
        if selected_date < date.today():
            connection.close()
            return "ไม่สามารถจองวันที่ผ่านมาแล้วได้", 400

        # 4. จำกัดเวลาให้ตรงกับช่วงที่ร้านเปิด
        if booking_time not in time_slots:
            connection.close()
            return "เวลานี้ไม่อยู่ในช่วงที่เปิดให้จอง", 400

        # 5. ห้ามจองเวลาที่ผ่านไปแล้วในวันนี้
        selected_datetime = datetime.combine(
            selected_date, selected_time
        )

        if selected_datetime <= datetime.now():
            connection.close()
            return "ไม่สามารถจองเวลาในอดีตได้", 400

        # 6. ตรวจสอบว่าแมวเป็นของสมาชิกคนนี้
        cat = connection.execute("""
            SELECT cat_id
            FROM cats
            WHERE cat_id = ? AND user_id = ?

        """, (cat_id, session["user_id"])).fetchone()

        if cat is None:
            connection.close()
            return "ไม่พบข้อมูลน้องแมวของคุณ", 403

        # 7. เริ่ม transaction เพื่อป้องกันการจองซ้ำ
        connection.execute("BEGIN IMMEDIATE")
        existing_booking = connection.execute("""
            SELECT booking_id
            FROM bookings
            WHERE booking_date = ?
              AND booking_time = ?
              AND status IN ('รอยืนยัน', 'ยืนยันแล้ว')
            LIMIT 1

        """, (booking_date, booking_time)).fetchone()

        if existing_booking:
            connection.rollback()
            connection.close()

            return (
                "ขออภัย เวลานี้มีผู้จองแล้ว "
                "กรุณาเลือกวันหรือเวลาอื่น",
                409
            )

        # =========================================================================
        # 8. คำนวณระยะทางและค่าบริการรับ-ส่งน้องแมว (Pet Taxi Service)
        # คำนวณจากพิกัดร้านใกล้คณะศึกษาศาสตร์ ม.ขอนแก่น ไปยังจุดที่ลูกค้าปักหมุด
        # =========================================================================
        delivery_type = request.form.get("delivery_type", "none").strip()
        pickup_address = request.form.get("pickup_address", "").strip() if delivery_type != "none" else ""
        latitude = request.form.get("latitude", type=float) if delivery_type != "none" else None
        longitude = request.form.get("longitude", type=float) if delivery_type != "none" else None
        delivery_notes = request.form.get("delivery_notes", "").strip() if delivery_type != "none" else ""
        distance_km = 0.0
        delivery_fee = 0

        if delivery_type != "none" and latitude is not None and longitude is not None:
            # คำนวณระยะทางจริงจากร้าน (ใกล้คณะศึกษาศาสตร์ มข.) ไปยังบ้านลูกค้า
            distance_km = calculate_distance_km(SHOP_LAT, SHOP_LNG, latitude, longitude)
            delivery_fee = calculate_delivery_fee(delivery_type, distance_km)
        else:
            delivery_type = "none"
            delivery_fee = 0
            distance_km = 0.0

        # รวมราคาสุทธิ (ค่าบริการสปา + ค่าบริการรับ-ส่งตามระยะทาง)
        total_price = int(package["price"]) + int(delivery_fee)

        # =========================================================================
        # 9. จัดการระบบชำระเงิน (Payment Method: ชำระหน้าร้าน vs สแกน QR Code)
        # กฎ: หากเลือกบริการรับและส่ง (round_trip) ต้องชำระเงินโดยการสแกน QR Code เท่านั้น
        #     หากเลือกรับเที่ยวเดียว, ส่งเที่ยวเดียว หรือพาน้องมาเอง สามารถเลือกได้ทั้ง 2 แบบ
        # =========================================================================
        payment_method = request.form.get("payment_method", "pay_at_shop").strip()

        if delivery_type == "round_trip":
            payment_method = "qr_code"
        elif payment_method not in ("pay_at_shop", "qr_code"):
            payment_method = "pay_at_shop"
        payment_slip = ""
        slip_uploaded_at = ""

        if payment_method == "qr_code":
            slip_file = request.files.get("payment_slip")

            if slip_file and slip_file.filename and allowed_file(slip_file.filename):
                ext = slip_file.filename.rsplit(".", 1)[-1].lower()
                slip_filename = f"slip_{uuid.uuid4().hex}.{ext}"
                slip_path = os.path.join(app.config["UPLOAD_FOLDER"], slip_filename)
                slip_file.save(slip_path)
                payment_slip = slip_filename
                slip_uploaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                payment_status = "รอตรวจสอบสลิป"
            else:
                payment_status = "รอแนบสลิป"
        else:
            # เลือกชำระเงินหน้าร้าน (เหมาะสำหรับรับส่งเอง หรือชำระเมื่อถึงร้าน)
            payment_method = "pay_at_shop"
            payment_status = "รอชำระหน้าร้าน"

        # เลือกพนักงานผู้ให้บริการ (Staff Selection)
        staff_id = request.form.get("staff_id", type=int)
        staff_name = None

        if staff_id:
            st = get_staff_by_id(staff_id)

            if st:
                staff_name = st["nickname"]
            else:
                staff_id = None

        # 10. บันทึกข้อมูลการจองลงฐานข้อมูล พร้อมพิกัด ระยะทาง ข้อมูลการชำระเงิน และพนักงานที่เลือก
        connection.execute("""
            INSERT INTO bookings (
                user_id,
                cat_id,
                service_name,
                service_description,
                price,
                booking_date,
                booking_time,
                notes,
                status,
                delivery_type,
                delivery_fee,
                pickup_address,
                latitude,
                longitude,
                delivery_notes,
                distance_km,
                payment_method,
                payment_status,
                payment_slip,
                slip_uploaded_at,
                notification_read,
                staff_id,
                staff_name,
                has_reviewed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (
            session["user_id"],
            cat_id,
            package["name"],
            package["description"],
            total_price,
            booking_date,
            booking_time,
            notes,
            "รอยืนยัน",
            delivery_type,
            delivery_fee,
            pickup_address,
            latitude,
            longitude,
            delivery_notes,
            distance_km,
            payment_method,
            payment_status,
            payment_slip,
            slip_uploaded_at,
            0,
            staff_id,
            staff_name,
            0
        ))
        connection.commit()
        connection.close()
        flash("สร้างรายการจองเรียบร้อยแล้ว", "success")

        return redirect(url_for("bookings"))

    connection.close()
    staff_list = get_staff_list()
    preselected_staff_id = request.args.get("staff_id", type=int)

    return render_template(
        "new_booking.html",
        cats=cats,
        services=services,
        categories=SERVICE_CATEGORIES,
        time_slots=time_slots,
        staff_list=staff_list,
        preselected_staff_id=preselected_staff_id,
        shop_lat=SHOP_LAT,
        shop_lng=SHOP_LNG,
        shop_name=SHOP_NAME,
        shop_address=SHOP_ADDRESS,
        shop_promptpay=SHOP_PROMPTPAY
    )

# =========================================================================
# Route: อัปโหลดสลิปหลักฐานการโอนเงิน (สำหรับลูกค้าในหน้าการจองของฉัน)
# =========================================================================
@app.route("/bookings/<int:booking_id>/upload-slip", methods=["POST"])
def upload_booking_slip(booking_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    booking = connection.execute(
        "SELECT * FROM bookings WHERE booking_id = ? AND user_id = ?",
        (booking_id, session["user_id"])
    ).fetchone()

    if not booking:
        connection.close()
        flash("ไม่พบรายการจองที่ระบุ", "error")
        return redirect(url_for("bookings"))

    slip_file = request.files.get("payment_slip")

    if not slip_file or not slip_file.filename or not allowed_file(slip_file.filename):
        connection.close()
        flash("กรุณาเลือกไฟล์รูปภาพสลิปที่ถูกต้อง (JPG, PNG, WEBP)", "error")
        return redirect(url_for("bookings"))

    ext = slip_file.filename.rsplit(".", 1)[-1].lower()
    slip_filename = f"slip_{uuid.uuid4().hex}.{ext}"
    slip_path = os.path.join(app.config["UPLOAD_FOLDER"], slip_filename)
    slip_file.save(slip_path)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    connection.execute("""
        UPDATE bookings
        SET payment_slip = ?, slip_uploaded_at = ?, payment_status = 'รอตรวจสอบสลิป', payment_method = 'qr_code', notification_read = 1
        WHERE booking_id = ?

    """, (slip_filename, now_str, booking_id))
    connection.commit()
    connection.close()
    flash("แนบสลิปการโอนเงินเรียบร้อยแล้ว แอดมินจะตรวจสอบยอดเงินให้โดยเร็ว", "success")
    return redirect(url_for("bookings"))


# =========================================================================
# Route: ลูกค้ารับทราบการแจ้งเตือน (ปิดการแจ้งเตือนในระบบ)
# =========================================================================
@app.route("/bookings/<int:booking_id>/dismiss-notification", methods=["POST"])
def dismiss_notification(booking_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    connection.execute("""
        UPDATE bookings
        SET notification_read = 1
        WHERE booking_id = ? AND user_id = ?

    """, (booking_id, session["user_id"]))
    connection.commit()
    connection.close()
    flash("รับทราบการแจ้งเตือนเรียบร้อยแล้วค่ะ", "info")
    return redirect(request.referrer or url_for("dashboard"))

# =========================================================================
# Route: หน้ารวมทีมงานพนักงานผู้เชี่ยวชาญ (Staff Team Showcase)
# =========================================================================
@app.route("/staff", endpoint="staff_page")
def staff_page():
    staff_list = get_staff_list()
    connection = get_db_connection()
    try:
        # ดึงรีวิวล่าสุดของร้านและพนักงานมาแสดงในหน้าทีมงาน
        shop_reviews = connection.execute("""
            SELECT review_id, user_name, cat_name, shop_rating, shop_comment, staff_name, staff_rating, service_name, created_at
            FROM reviews
            WHERE (shop_comment IS NOT NULL AND shop_comment != '')
               OR (staff_comment IS NOT NULL AND staff_comment != '')
            ORDER BY review_id DESC LIMIT 12
        """).fetchall()
        shop_reviews = []
        for r in shop_reviews:
            rd = dict(r)
            rd["masked_user_name"] = mask_customer_name(rd.get("user_name", ""))
            shop_reviews.append(rd)
    finally:
        connection.close()
    return render_template(
        "staff.html",
        staff_list=staff_list,
        shop_reviews=shop_reviews
    )

# =========================================================================
# API: ดึงรีวิวของพนักงานรายบุคคล (AJAX / Modal)
# =========================================================================
@app.route("/api/staff/<int:staff_id>/reviews", endpoint="api_staff_reviews")
def api_staff_reviews(staff_id):
    staff = get_staff_by_id(staff_id)
    if not staff:
        return jsonify({"error": "Staff not found"}), 404
    connection = get_db_connection()
    try:
        revs = connection.execute("""
            SELECT user_name, cat_name, staff_rating, staff_comment, service_name, created_at
            FROM reviews
            WHERE staff_id = ? AND staff_comment IS NOT NULL AND staff_comment != ''
            ORDER BY review_id DESC
        """, (staff_id,)).fetchall()
        return jsonify({
            "staff": staff,
            "reviews": [dict(r) for r in revs]
        })
    finally:
        connection.close()

# =========================================================================
# Route: ลูกค้ารีวิวบริการและพนักงาน (Shop & Staff Review System)
# =========================================================================
@app.route("/bookings/<int:booking_id>/review", methods=["GET", "POST"], endpoint="review_booking")
def review_booking(booking_id):
    if "user_id" not in session:
        flash("กรุณาเข้าสู่ระบบก่อนทำการรีวิวบริการค่ะ", "info")
        return redirect(url_for("login"))
    
    connection = get_db_connection()

    try:
        booking = connection.execute("""
            SELECT b.*, c.cat_name, c.breed, c.image AS cat_image, u.name AS customer_name
            FROM bookings b
            JOIN cats c ON b.cat_id = c.cat_id
            JOIN users u ON b.user_id = u.user_id
            WHERE b.booking_id = ? AND b.user_id = ?

        """, (booking_id, session["user_id"])).fetchone()

        if not booking:
            flash("ไม่พบรายการจองนี้ หรือคุณไม่มีสิทธิ์เข้าถึงค่ะ", "error")
            return redirect(url_for("bookings"))

        if booking["status"] != "เสร็จสิ้น":
            flash("คุณสามารถรีวิวได้เฉพาะบริการที่เสร็จสิ้นเรียบร้อยแล้วเท่านั้นค่ะ", "warning")
            return redirect(url_for("bookings"))

        if booking["has_reviewed"]:
            flash("คุณได้ทำการรีวิวรายการบริการนี้เรียบร้อยแล้ว ขอบคุณสำหรับความคิดเห็นค่ะ ♡", "info")
            return redirect(url_for("bookings"))

        # ข้อมูลพนักงานที่ดูแล (ถ้ามี)
        staff = None

        if booking["staff_id"]:
            staff = connection.execute("""
                SELECT * FROM staff WHERE staff_id = ?
            """, (booking["staff_id"],)).fetchone()

            if staff:
                staff = dict(staff)

        if request.method == "POST":
            shop_rating = request.form.get("shop_rating", type=int)
            shop_comment = request.form.get("shop_comment", "").strip()
            staff_rating = request.form.get("staff_rating", type=int)
            staff_comment = request.form.get("staff_comment", "").strip()

            if not shop_rating or shop_rating < 1 or shop_rating > 5:
                flash("กรุณาให้คะแนนความพึงพอใจต่อร้านค้า (1 - 5 ดาว) ค่ะ", "error")
                return render_template("review_booking.html", booking=booking, staff=staff)

            # หากมีพนักงานแต่ลูกค้าไม่ได้ระบุคะแนนพนักงาน ให้ใช้คะแนนเดียวกับร้าน
            if staff and (not staff_rating or staff_rating < 1 or staff_rating > 5):
                staff_rating = shop_rating
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            connection.execute("""
                INSERT INTO reviews (
                    booking_id, user_id, user_name, cat_name,
                    staff_id, staff_name, service_name,
                    shop_rating, shop_comment,
                    staff_rating, staff_comment,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            """, (
                booking_id,
                session["user_id"],
                session.get("name", booking["customer_name"]),
                booking["cat_name"],
                booking["staff_id"],
                booking["staff_name"] or (staff["nickname"] if staff else None),
                booking["service_name"],
                shop_rating,
                shop_comment,
                staff_rating,
                staff_comment,
                now_str
            ))
            connection.execute("""
                UPDATE bookings
                SET has_reviewed = 1
                WHERE booking_id = ?
            """, (booking_id,))

            # คำนวณคะแนนเฉลี่ยใหม่ของพนักงานคนนี้
            if booking["staff_id"]:
                avg_res = connection.execute("""
                    SELECT AVG(staff_rating)
                    FROM reviews
                    WHERE staff_id = ? AND staff_rating IS NOT NULL
                """, (booking["staff_id"],)).fetchone()

                if avg_res and avg_res[0] is not None:
                    new_rating = round(float(avg_res[0]), 1)
                    connection.execute("""
                        UPDATE staff
                        SET rating = ?
                        WHERE staff_id = ?
                    """, (new_rating, booking["staff_id"]))
            connection.commit()
            flash("🌟 ขอบพระคุณสำหรับรีวิวและความคิดเห็นอันมีค่ายิ่ง! ทุกคะแนนของท่านช่วยให้ Cat Spa และพี่ๆ พนักงานพัฒนาการดูแลน้องแมวให้ดียิ่งขึ้นค่ะ ♡", "success")

            return redirect(url_for("bookings"))

        return render_template("review_booking.html", booking=booking, staff=staff)
    finally:
        connection.close()


# =========================================================================
# Route: พิมพ์ใบเสร็จรับเงิน (เมื่อชำระเงินผ่าน QR Code และแอดมินตรวจสอบสลิปแล้ว)
# =========================================================================
@app.route("/bookings/<int:booking_id>/receipt")
def print_receipt(booking_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    is_admin = session.get("role") == "admin"

    if is_admin:
        booking = connection.execute("""
            SELECT b.*, c.cat_name, c.breed, c.gender, c.age, c.weight,
                   u.name AS customer_name, u.phone AS customer_phone, u.email AS customer_email
            FROM bookings b
            LEFT JOIN cats c ON b.cat_id = c.cat_id
            LEFT JOIN users u ON b.user_id = u.user_id
            WHERE b.booking_id = ?

        """, (booking_id,)).fetchone()
    else:
        booking = connection.execute("""
            SELECT b.*, c.cat_name, c.breed, c.gender, c.age, c.weight,
                   u.name AS customer_name, u.phone AS customer_phone, u.email AS customer_email
            FROM bookings b
            LEFT JOIN cats c ON b.cat_id = c.cat_id
            LEFT JOIN users u ON b.user_id = u.user_id
            WHERE b.booking_id = ? AND b.user_id = ?

        """, (booking_id, session["user_id"])).fetchone()
    connection.close()

    if not booking:
        flash("ไม่พบข้อมูลการจองที่ต้องการออกใบเสร็จ", "error")
        return redirect(url_for("bookings") if not is_admin else url_for("admin_bookings"))

    # เงื่อนไข: สแกนคิวอาร์โค้ด และได้รับการยืนยันสลิปที่ลูกค้าส่งมาผ่านการตรวจเช็คเรียบร้อยแล้ว
    if not is_admin:
        if booking["payment_method"] != "qr_code" or booking["payment_status"] != "ชำระเงินแล้ว":
            flash("ใบเสร็จรับเงินจะสามารถพิมพ์ได้เมื่อชำระเงินผ่าน QR Code และแอดมินยืนยันยอดเงินผ่านการตรวจสอบสลิปแล้วเท่านั้นค่ะ", "warning")
            return redirect(url_for("bookings"))

    # คำนวณราคาบริการหลัก (หักค่ารับส่ง)
    delivery_fee = booking["delivery_fee"] or 0
    total_price = booking["price"] or 0
    service_price = total_price - delivery_fee

    if service_price < 0:
        service_price = total_price
    date_str = (booking["booking_date"] or "").replace("-", "")
    receipt_no = f"REC-{date_str}-{booking['booking_id']:04d}"

    return render_template(
        "receipt.html",
        b=booking,
        service_price=service_price,
        receipt_no=receipt_no,
        shop_name=SHOP_NAME,
        shop_address=SHOP_ADDRESS,
        shop_promptpay=SHOP_PROMPTPAY,
        today_date=datetime.now().strftime("%d/%m/%Y")
    )


# =========================================================================
# Route: ดูไฟล์รูปภาพสลิปหลักฐานการชำระเงิน
# =========================================================================
@app.route("/uploads/slip/<filename>")
def uploaded_payment_slip(filename):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") == "admin":
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    connection = get_db_connection()
    booking = connection.execute(
        "SELECT booking_id FROM bookings WHERE payment_slip = ? AND user_id = ?",
        (filename, session["user_id"])
    ).fetchone()
    connection.close()

    if booking is None:
        abort(403)
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# =========================================================================
# Route: อัปเดตสถานะการชำระเงิน (สำหรับ Admin ตรวจสอบสลิปและยืนยันยอดเงิน)
# =========================================================================

@app.route("/admin/bookings/<int:booking_id>/update-payment", methods=["POST"])
@admin_required
def admin_update_payment_status(booking_id):
    new_status = request.form.get("payment_status", "").strip()
    allowed_statuses = ["รอชำระหน้าร้าน", "รอตรวจสอบสลิป", "ชำระเงินแล้ว", "สลิปไม่ถูกต้อง"]

    if new_status not in allowed_statuses:
        flash("สถานะการชำระเงินไม่ถูกต้อง", "error")
        return redirect(request.referrer or url_for("admin_bookings"))

    # หากแอดมินแจ้งว่าสลิปไม่ถูกต้อง ให้ตั้ง notification_read = 0 เพื่อเตือนลูกค้าทันที
    notif_read_val = 0 if new_status == "สลิปไม่ถูกต้อง" else 1
    connection = get_db_connection()
    connection.execute(
        "UPDATE bookings SET payment_status = ?, notification_read = ? WHERE booking_id = ?",
        (new_status, notif_read_val, booking_id)
    )
    connection.commit()
    connection.close()

    # หากพนักงานยืนยันสลิปถูกต้องแล้ว ('ชำระเงินแล้ว') ให้ส่งสลิปและใบเสร็จไปยังอีเมลของลูกค้าอัตโนมัติ
    if new_status == "ชำระเงินแล้ว":
        sent_ok, err = send_receipt_email(booking_id)
        if sent_ok:
            flash("✓ ยืนยันสลิปสำเร็จ! อัปเดตสถานะเป็น 'ชำระเงินแล้ว' และส่งใบเสร็จรับเงินไปยังอีเมลของลูกค้าเรียบร้อยแล้ว ✉️", "success")
        else:
            sender_email, app_pwd = get_email_credentials()

            if not app_pwd:
                flash(f"✓ ยืนยันสลิปสำเร็จ! อัปเดตสถานะเป็น 'ชำระเงินแล้ว' (ยังไม่ได้ส่งอีเมลเนื่องจากยังไม่ตั้งค่ารหัสผ่าน {sender_email} ใน email_config.json)", "info")
            else:
                flash(f"✓ ยืนยันสลิปสำเร็จ! อัปเดตสถานะเป็น 'ชำระเงินแล้ว' (ส่งอีเมลไม่สำเร็จ: {err})", "info")
    else:
        flash(f"อัปเดตสถานะการชำระเงินของการจอง #{booking_id} เป็น '{new_status}' สำเร็จ", "success")
    return redirect(request.referrer or url_for("admin_bookings"))

# =========================================================================
# Route: ส่งใบเสร็จรับเงินเข้าอีเมล (สำหรับลูกค้า หรือ แอดมินกดส่งซ้ำ)
# =========================================================================
@app.route("/bookings/<int:booking_id>/send-receipt", methods=["POST"])
def send_receipt_to_email(booking_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    is_admin = session.get("role") == "admin"
    if is_admin:
        booking = connection.execute("SELECT * FROM bookings WHERE booking_id = ?", (booking_id,)).fetchone()
    else:
        booking = connection.execute("SELECT * FROM bookings WHERE booking_id = ? AND user_id = ?", (booking_id, session["user_id"])).fetchone()
    connection.close()

    if not booking:
        flash("ไม่พบข้อมูลการจอง", "error")
        return redirect(url_for("bookings") if not is_admin else url_for("admin_bookings"))

    if not is_admin and (booking["payment_method"] != "qr_code" or booking["payment_status"] != "ชำระเงินแล้ว"):
        flash("สามารถส่งใบเสร็จได้เมื่อยืนยันการชำระเงินผ่าน QR Code เรียบร้อยแล้วเท่านั้นค่ะ", "warning")
        return redirect(url_for("bookings"))

    success, err = send_receipt_email(booking_id)

    if success:
        flash("ระบบได้ส่งใบเสร็จรับเงินไปยังอีเมลของคุณเรียบร้อยแล้วค่ะ ✉️ กรุณาตรวจสอบกล่องข้อความ", "success")
    else:
        sender_email, app_pwd = get_email_credentials()

        if not app_pwd:
            flash(f"⚠️ ระบบยังไม่ได้เชื่อมต่อรหัสผ่านอีเมลผู้ส่ง ({sender_email}) ใน email_config.json", "warning")
        else:
            flash(f"⚠️ ไม่สามารถส่งอีเมลได้: {err}", "error")
    return redirect(url_for("print_receipt", booking_id=booking_id))


@app.route("/bookings/available-times")
def available_times():
    if "user_id" not in session:
        return jsonify({"error": "กรุณาเข้าสู่ระบบ"}), 401

    booking_date = request.args.get("date", "")

    try:
        selected_date = datetime.strptime(
            booking_date, "%Y-%m-%d"
        ).date()
    except ValueError:
        return jsonify({"error": "วันที่ไม่ถูกต้อง"}), 400

    if selected_date < date.today():
        return jsonify({"error": "ไม่สามารถเลือกวันที่ย้อนหลัง"}), 400

    time_slots = [
        "09:00", "10:00", "11:00",
        "13:00", "14:00", "15:00",
        "16:00", "17:00", "18:00", "19:00"
    ]
    connection = get_db_connection()
    rows = connection.execute("""
        SELECT booking_time
        FROM bookings
        WHERE booking_date = ?
          AND status IN ('รอยืนยัน', 'ยืนยันแล้ว')

    """, (booking_date,)).fetchall()
    connection.close()
    booked_times = {row["booking_time"] for row in rows}
    available = []

    for slot in time_slots:
        slot_time = datetime.strptime(slot, "%H:%M").time()
        slot_datetime = datetime.combine(selected_date, slot_time)

        # ไม่แสดงเวลาที่ผ่านไปแล้วในวันนี้
        if slot_datetime <= datetime.now():
            continue

        # ไม่แสดงเวลาที่มีคิวอยู่แล้ว
        if slot not in booked_times:
            available.append(slot)
    return jsonify({"available_times": available})


@app.route("/bookings/cancel/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    connection.execute("""
        UPDATE bookings
        SET status = 'ยกเลิกแล้ว'
        WHERE booking_id = ?
          AND user_id = ?
          AND status = 'รอยืนยัน'
    """, (booking_id, session["user_id"]))
    connection.commit()
    connection.close()

    return redirect(url_for("bookings"))

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy_policy.html")

# รายละเอียดบริการแต่ละหมวด

@app.route("/service/<service_id>")
def service_detail(service_id):
    service_metadata = {
        "bath": {
            "name": "อาบน้ำแมว",
            "icon": "🛁",
            "subtitle": "ทำความสะอาดขนและผิวหนังอย่างอ่อนโยน",
            "description": "เหมาะสำหรับแมวที่ต้องการดูแลความสะอาดเป็นประจำ",
            "category_db": "อาบน้ำแมว",
            "included": [
                "ตรวจสภาพขนและผิวหนังก่อนให้บริการ",
                "ใช้แชมพูที่เหมาะกับแมว",
                "ล้างแชมพูออกให้สะอาด",
                "เช็ดตัวและเป่าขนให้แห้ง",
                "หวีขนและตรวจความเรียบร้อย"
            ],
            "notes": [
                "ราคาขึ้นอยู่กับความยาวขนและสภาพขน",
                "ขนพันกันมากหรือมีปัญหาผิวหนัง อาจต้องประเมินก่อนให้บริการ"
            ]
        },
        "spa": {
            "name": "สปาแมว",
            "icon": "🧴",
            "subtitle": "เพิ่มการดูแลขนและผิวหนังให้กับน้องแมว",
            "description": "เลือกแพ็กเกจตามระดับการดูแลที่ต้องการ",
            "category_db": "สปาแมว",
            "included": [
                "ตรวจสภาพขนและผิวหนังเบื้องต้น",
                "ทำความสะอาดขน",
                "บำรุงขนตามแพ็กเกจที่เลือก",
                "เป่าขนและหวีขนให้เรียบร้อย"
            ],
            "notes": [
                "ผลิตภัณฑ์ต้องเหมาะสำหรับแมวโดยเฉพาะ",
                "บริการนี้ไม่ใช่การรักษาโรคผิวหนัง หากพบความผิดปกติควรปรึกษาสัตวแพทย์"
            ]
        },
        "haircut": {
            "name": "ตัดแต่งขน",
            "icon": "✂️",
            "subtitle": "เลือกทรงที่เหมาะกับน้องแมว",
            "description": "ราคาแตกต่างตามรูปแบบการตัดและสภาพขน",
            "category_db": "ตัดแต่งขน",
            "included": [
                "ตรวจสภาพขนก่อนตัด",
                "เลือกทรงร่วมกับเจ้าของ",
                "ตัดแต่งขนตามรายการที่เลือก",
                "ตรวจความเรียบร้อยหลังตัด"
            ],
            "notes": [
                "ราคาเป็นตัวอย่างสำหรับขนที่สามารถตัดได้ตามปกติ",
                "ขนพันกันแน่นมากอาจต้องประเมินความปลอดภัยก่อนตัด",
                "ไม่รับประกันทรงเหมือนภาพตัวอย่างทุกประการ เพราะขึ้นอยู่กับสภาพขนของแมว"
            ]
        },
        "nails": {
            "name": "ตัดเล็บ",
            "icon": "🐾",
            "subtitle": "ดูแลเล็บและอุ้งเท้าอย่างระมัดระวัง",
            "description": "เลือกบริการดูแลเล็บตามความต้องการ",
            "category_db": "ตัดเล็บ",
            "included": [
                "ตรวจเล็บและอุ้งเท้าก่อนเริ่ม",
                "ตัดเฉพาะส่วนปลายเล็บอย่างระมัดระวัง",
                "ตรวจความเรียบร้อยหลังให้บริการ"
            ],
            "notes": [
                "หากแมวเครียดมากหรือไม่สามารถให้บริการได้อย่างปลอดภัย อาจต้องหยุดพัก",
                "หากพบเล็บผิดปกติหรืออุ้งเท้าบาดเจ็บ ควรปรึกษาสัตวแพทย์"
            ]
        }
    }
    meta = service_metadata.get(service_id)
    slug = service_id

    if not meta:
        for k, v in service_metadata.items():
            if v["name"] == service_id or v["category_db"] == service_id:
                meta = v
                slug = k
                break

    if not meta:
        return "ไม่พบบริการที่ต้องการ", 404

    # ดึงคอร์สจาก SQLite database services table แบบ Dynamic ตาม category!
    connection = get_db_connection()
    rows = connection.execute("""
        SELECT service_id, category, service_name, description, price
        FROM services
        WHERE (category = ? OR category = ?) AND is_active = 1
        ORDER BY price ASC

    """, (meta["category_db"], slug)).fetchall()
    connection.close()
    pricing = []

    for r in rows:
        pricing.append({
            "service_id": r["service_id"],
            "name": r["service_name"],
            "price": r["price"],
            "description": r["description"] or ""
        })
    service = dict(meta)
    service["pricing"] = pricing
    service["slug"] = slug

    return render_template(
        "service_detail.html",
        service=service
    )

# (admin_required decorator is defined at top of file)
# =====================================
# หน้า Dashboard สำหรับ Admin
# =====================================
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    connection = get_db_connection()
    today_str = date.today().strftime("%Y-%m-%d")
    total = connection.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    pending = connection.execute("SELECT COUNT(*) FROM bookings WHERE status = 'รอยืนยัน'").fetchone()[0]
    confirmed = connection.execute("SELECT COUNT(*) FROM bookings WHERE status = 'ยืนยันแล้ว'").fetchone()[0]
    completed = connection.execute("SELECT COUNT(*) FROM bookings WHERE status = 'เสร็จสิ้น'").fetchone()[0]
    rejected = connection.execute("SELECT COUNT(*) FROM bookings WHERE status = 'ปฏิเสธ'").fetchone()[0]
    revenue_res = connection.execute("SELECT SUM(price) FROM bookings WHERE status = 'เสร็จสิ้น'").fetchone()[0]
    revenue = revenue_res if revenue_res else 0
    total_members = connection.execute("SELECT COUNT(*) FROM users WHERE role = 'customer'").fetchone()[0]
    total_cats = connection.execute("SELECT COUNT(*) FROM cats").fetchone()[0]
    total_services = connection.execute("SELECT COUNT(*) FROM services WHERE is_active = 1").fetchone()[0]
    total_reviews = connection.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
    avg_shop_res = connection.execute("SELECT ROUND(AVG(shop_rating), 1) FROM reviews WHERE shop_rating IS NOT NULL").fetchone()[0]
    avg_shop_rating = avg_shop_res if avg_shop_res is not None else 5.0
    staff_count = connection.execute("SELECT COUNT(*) FROM staff WHERE is_active = 1").fetchone()[0]
    pending_bookings = connection.execute("""
        SELECT b.booking_id, b.service_name, b.service_description, b.price,
               b.booking_date, b.booking_time, b.status, b.notes,
               b.delivery_type, b.delivery_fee, b.pickup_address, b.latitude, b.longitude, b.delivery_notes,
               b.distance_km, b.payment_method, b.payment_status, b.payment_slip, b.slip_uploaded_at,
               c.cat_name, c.image AS cat_image, c.breed AS cat_breed,
               u.name AS customer_name, u.phone AS customer_phone
        FROM bookings b
        LEFT JOIN cats c ON b.cat_id = c.cat_id
        LEFT JOIN users u ON b.user_id = u.user_id
        WHERE b.status = 'รอยืนยัน'
        ORDER BY b.booking_date ASC, b.booking_time ASC
        LIMIT 5

    """).fetchall()
    today_bookings = connection.execute("""
        SELECT b.booking_id, b.service_name, b.service_description, b.price,
               b.booking_date, b.booking_time, b.status, b.notes,
               b.delivery_type, b.delivery_fee, b.pickup_address, b.latitude, b.longitude, b.delivery_notes,
               b.distance_km, b.payment_method, b.payment_status, b.payment_slip, b.slip_uploaded_at,
               c.cat_name, c.image AS cat_image, c.breed AS cat_breed,
               u.name AS customer_name, u.phone AS customer_phone
        FROM bookings b
        LEFT JOIN cats c ON b.cat_id = c.cat_id
        LEFT JOIN users u ON b.user_id = u.user_id
        WHERE b.booking_date = ?
        ORDER BY b.booking_time ASC
        LIMIT 5

    """, (today_str,)).fetchall()
    connection.close()

    return render_template(
        "admin_dashboard.html",
        total=total,
        pending=pending,
        confirmed=confirmed,
        completed=completed,
        rejected=rejected,
        revenue=revenue,
        total_members=total_members,
        total_cats=total_cats,
        total_services=total_services,
        total_reviews=total_reviews,
        avg_shop_rating=avg_shop_rating,
        staff_count=staff_count,
        pending_bookings=pending_bookings,
        today_bookings=today_bookings,
        today_str=today_str
    )

# =====================================
# หน้าจัดการการจองสำหรับ Admin
# =====================================
@app.route("/admin/bookings")
@admin_required
def admin_bookings():
    status_filter = request.args.get("status", "all").strip()
    keyword = request.args.get("q", "").strip()
    date_filter = request.args.get("date", "").strip()
    connection = get_db_connection()
    counts = {
        "all": connection.execute("SELECT COUNT(*) FROM bookings").fetchone()[0],
        "pending": connection.execute("SELECT COUNT(*) FROM bookings WHERE status = 'รอยืนยัน'").fetchone()[0],
        "confirmed": connection.execute("SELECT COUNT(*) FROM bookings WHERE status = 'ยืนยันแล้ว'").fetchone()[0],
        "completed": connection.execute("SELECT COUNT(*) FROM bookings WHERE status = 'เสร็จสิ้น'").fetchone()[0],
        "rejected": connection.execute("SELECT COUNT(*) FROM bookings WHERE status = 'ปฏิเสธ'").fetchone()[0]
    }
    where_clauses = ["1=1"]
    params = []

    if status_filter and status_filter != "all":
        where_clauses.append("b.status = ?")
        params.append(status_filter)

    if keyword:
        where_clauses.append("(u.name LIKE ? OR c.cat_name LIKE ? OR b.service_name LIKE ? OR u.phone LIKE ?)")
        kw = f"%{keyword}%"
        params.extend([kw, kw, kw, kw])

    if date_filter:
        where_clauses.append("b.booking_date = ?")
        params.append(date_filter)
    bookings = connection.execute(f"""
        SELECT
            b.booking_id,
            b.user_id,
            b.cat_id,
            b.service_name,
            b.service_description,
            b.price,
            b.booking_date,
            b.booking_time,
            b.notes,
            b.status,
            b.created_at,
            b.delivery_type,
            b.delivery_fee,
            b.pickup_address,
            b.latitude,
            b.longitude,
            b.delivery_notes,
            b.distance_km,
            b.payment_method,
            b.payment_status,
            b.payment_slip,
            b.slip_uploaded_at,
            b.staff_id,
            b.staff_name,
            b.has_reviewed,
            c.cat_name,
            c.image AS cat_image,
            c.breed AS cat_breed,
            u.name AS customer_name,
            u.email AS customer_email,
            u.phone AS customer_phone
        FROM bookings b
        LEFT JOIN cats c ON b.cat_id = c.cat_id
        LEFT JOIN users u ON b.user_id = u.user_id
        WHERE {' AND '.join(where_clauses)}
        ORDER BY b.booking_date DESC, b.booking_time DESC, b.booking_id DESC

    """, params).fetchall()
    connection.close()

    return render_template(
        "admin_bookings.html",
        bookings=bookings,
        counts=counts,
        current_status=status_filter,
        keyword=keyword,
        date_filter=date_filter
    )

# =========================================================================
# Route: จัดการพนักงานในร้านสำหรับแอดมิน (Admin Staff Management)
# =========================================================================
@app.route("/admin/staff", endpoint="admin_staff")
@admin_required
def admin_staff():
    connection = get_db_connection()

    try:
        staff_rows = connection.execute("""
            SELECT s.*,
                   (SELECT COUNT(*) FROM reviews r WHERE r.staff_id = s.staff_id) AS review_count,
                   (SELECT ROUND(AVG(r.staff_rating), 1) FROM reviews r WHERE r.staff_id = s.staff_id AND r.staff_rating IS NOT NULL) AS avg_staff_rating
            FROM staff s
            ORDER BY s.staff_id ASC

        """).fetchall()
        staff_list = [dict(r) for r in staff_rows]

        for s in staff_list:
            if s.get("specialties"):
                s["specialty_list"] = [sp.strip() for sp in s["specialties"].split(",") if sp.strip()]
            else:
                s["specialty_list"] = []
    finally:
        connection.close()
    return render_template("admin_staff.html", staff_list=staff_list)


@app.route("/admin/staff/<int:staff_id>/edit", methods=["GET", "POST"], endpoint="admin_staff_edit")
@admin_required
def admin_staff_edit(staff_id):
    connection = get_db_connection()
    try:
        staff = connection.execute("SELECT * FROM staff WHERE staff_id = ?", (staff_id,)).fetchone()

        if not staff:
            flash("ไม่พบข้อมูลพนักงานที่ต้องการแก้ไข", "error")
            return redirect(url_for("admin_staff"))

        if request.method == "POST":
            nickname = request.form.get("nickname", "").strip()
            role_title = request.form.get("role_title", "").strip()
            specialties = request.form.get("specialties", "").strip()
            highlights = request.form.get("highlights", "").strip()
            experience_years = request.form.get("experience_years", type=int) or 1
            status_text = request.form.get("status_text", "พร้อมให้บริการ").strip()
            is_active = 1 if request.form.get("is_active") == "1" else 0

            if not nickname:
                flash("กรุณาระบุชื่อเล่นของพนักงาน", "error")
                return render_template("admin_staff_edit.html", staff=dict(staff))

            image_name = staff["image"]
            new_image = request.files.get("image")

            if new_image and new_image.filename and allowed_file(new_image.filename):
                ext = new_image.filename.rsplit(".", 1)[-1].lower()
                image_name = f"staff_{staff_id}_{uuid.uuid4().hex[:8]}.{ext}"
                new_image.save(os.path.join(app.static_folder, "images", image_name))
            connection.execute("""
                UPDATE staff
                SET name = ?,
                    nickname = ?,
                    role_title = ?,
                    specialties = ?,
                    highlights = ?,
                    experience_years = ?,
                    status_text = ?,
                    is_active = ?,
                    image = ?
                WHERE staff_id = ?

            """, (
                nickname,
                nickname,
                role_title,
                specialties,
                highlights,
                experience_years,
                status_text,
                is_active,
                image_name,
                staff_id
            ))
            connection.commit()
            flash(f"✅ บันทึกการแก้ไขข้อมูลคุณ{nickname} เรียบร้อยแล้ว", "success")

            return redirect(url_for("admin_staff"))

        return render_template("admin_staff_edit.html", staff=dict(staff))
    finally:
        connection.close()

# =========================================================================
# Route: ภาพรวมการรีวิวของลูกค้าสำหรับแอดมิน (Admin Customer Reviews Overview)
# =========================================================================
@app.route("/admin/reviews", endpoint="admin_reviews")
@admin_required
def admin_reviews():
    staff_id_filter = request.args.get("staff_id", "all").strip()
    rating_filter = request.args.get("rating", "all").strip()
    connection = get_db_connection()
    try:
        # สรุปคะแนนรีวิวร้านค้าภาพรวม
        total_reviews = connection.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
        avg_shop_res = connection.execute("SELECT ROUND(AVG(shop_rating), 1) FROM reviews WHERE shop_rating IS NOT NULL").fetchone()[0]
        avg_shop_rating = avg_shop_res if avg_shop_res is not None else 5.0
        avg_staff_res = connection.execute("SELECT ROUND(AVG(staff_rating), 1) FROM reviews WHERE staff_rating IS NOT NULL").fetchone()[0]
        avg_staff_rating = avg_staff_res if avg_staff_res is not None else 5.0

        # สรุปรีวิวแยกตามพนักงานแต่ละท่าน
        staff_summary = connection.execute("""
            SELECT s.staff_id, s.nickname, s.image, s.role_title,
                   COUNT(r.review_id) AS rev_count,
                   ROUND(AVG(r.staff_rating), 1) AS staff_avg
            FROM staff s
            LEFT JOIN reviews r ON s.staff_id = r.staff_id
            GROUP BY s.staff_id
            ORDER BY s.staff_id ASC
        """).fetchall()

        # กรองรายการรีวิว
        where_clauses = ["1=1"]
        params = []

        if staff_id_filter and staff_id_filter != "all":
            where_clauses.append("r.staff_id = ?")
            params.append(int(staff_id_filter))

        if rating_filter and rating_filter != "all":
            where_clauses.append("r.shop_rating = ?")
            params.append(int(rating_filter))
        reviews_query = f"""
            SELECT r.*, b.booking_date, b.booking_time
            FROM reviews r
            LEFT JOIN bookings b ON r.booking_id = b.booking_id
            WHERE {' AND '.join(where_clauses)}
            ORDER BY r.review_id DESC

        """
        review_rows = connection.execute(reviews_query, params).fetchall()
        reviews = [dict(r) for r in review_rows]
    finally:
        connection.close()
    return render_template(
        "admin_reviews.html",
        reviews=reviews,
        total_reviews=total_reviews,
        avg_shop_rating=avg_shop_rating,
        avg_staff_rating=avg_staff_rating,
        staff_summary=staff_summary,
        selected_staff_id=staff_id_filter,
        selected_rating=rating_filter
    )


@app.route("/admin/reviews/<int:review_id>/delete", methods=["POST"], endpoint="admin_delete_review")
@admin_required
def admin_delete_review(review_id):
    connection = get_db_connection()

    try:
        rev = connection.execute("SELECT * FROM reviews WHERE review_id = ?", (review_id,)).fetchone()

        if not rev:
            flash("ไม่พบข้อมูลรีวิวที่ต้องการลบ", "error")
            return redirect(url_for("admin_reviews"))

        staff_id = rev["staff_id"]
        booking_id = rev["booking_id"]
        connection.execute("DELETE FROM reviews WHERE review_id = ?", (review_id,))

        if booking_id:
            connection.execute("UPDATE bookings SET has_reviewed = 0 WHERE booking_id = ?", (booking_id,))

        # คำนวณคะแนนเฉลี่ยใหม่ของพนักงาน
        if staff_id:
            avg_res = connection.execute("""
                SELECT ROUND(AVG(staff_rating), 1)
                FROM reviews
                WHERE staff_id = ? AND staff_rating IS NOT NULL
            """, (staff_id,)).fetchone()[0]
            new_rating = avg_res if avg_res is not None else 5.0
            connection.execute("UPDATE staff SET rating = ? WHERE staff_id = ?", (new_rating, staff_id))
        connection.commit()
        flash("✓ ลบรายการรีวิวเรียบร้อยแล้ว และคำนวณคะแนนใหม่โดยอัตโนมัติ", "success")
    finally:
        connection.close()
    return redirect(url_for("admin_reviews"))

# =====================================
# จัดการบริการและราคา (Admin Course Management)
# =====================================
@app.route("/admin/services", methods=["GET", "POST"])
@admin_required
def admin_services():
    connection = get_db_connection()

    if request.method == "POST":
        category = request.form.get("category", "").strip()
        service_name = request.form.get("service_name", "").strip()
        description = request.form.get("description", "").strip()
        price_text = request.form.get("price", "").strip()

        try:
            price = int(price_text)

            if price < 0:
                raise ValueError
        except (ValueError, TypeError):
            connection.close()
            flash("กรุณากรอกราคาเป็นจำนวนเต็มตั้งแต่ 0 บาทขึ้นไป", "error")
            return redirect(url_for("admin_services"))

        if not category or not service_name:
            connection.close()
            flash("กรุณากรอกหมวดหมู่และชื่อบริการ", "error")
            return redirect(url_for("admin_services"))

        connection.execute("""
            INSERT INTO services
                (category, service_name, description, price, is_active)
            VALUES (?, ?, ?, ?, 1)

        """, (category, service_name, description, price))
        connection.commit()
        connection.close()
        flash(f"เพิ่มบริการ '{service_name}' เรียบร้อยแล้ว", "success")
        return redirect(url_for("admin_services"))

    category_filter = request.args.get("category", "all").strip()
    keyword = request.args.get("q", "").strip()
    where_clauses = ["1=1"]
    params = []

    if category_filter and category_filter != "all":
        where_clauses.append("category = ?")
        params.append(category_filter)

    if keyword:
        where_clauses.append("(service_name LIKE ? OR description LIKE ?)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    services = connection.execute(f"""
        SELECT * FROM services
        WHERE {' AND '.join(where_clauses)}
        ORDER BY category, price ASC

    """, params).fetchall()
    categories = ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"]
    connection.close()

    return render_template(
        "admin_services.html",
        services=services,
        categories=categories,
        current_category=category_filter,
        keyword=keyword
    )

# =====================================
# แก้ไขบริการและราคา
# =====================================
@app.route("/admin/services/<int:service_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_service(service_id):
    connection = get_db_connection()
    service = connection.execute("""
        SELECT * FROM services WHERE service_id = ?
    """, (service_id,)).fetchone()

    if service is None:
        connection.close()
        flash("ไม่พบบริการที่ต้องการแก้ไข", "error")
        return redirect(url_for("admin_services"))

    if request.method == "POST":
        category = request.form.get("category", "").strip()
        service_name = request.form.get("service_name", "").strip()
        description = request.form.get("description", "").strip()

        try:
            price = int(request.form.get("price", ""))

            if price < 0:
                raise ValueError
        except (ValueError, TypeError):
            connection.close()
            flash("กรุณากรอกราคาให้ถูกต้อง", "error")
            return redirect(url_for("edit_service", service_id=service_id))

        if not category or not service_name:
            connection.close()
            flash("กรุณากรอกหมวดหมู่และชื่อบริการ", "error")
            return redirect(url_for("edit_service", service_id=service_id))

        connection.execute("""
            UPDATE services
            SET category = ?,
                service_name = ?,
                description = ?,
                price = ?
            WHERE service_id = ?

        """, (category, service_name, description, price, service_id))
        connection.commit()
        connection.close()
        flash(f"แก้ไขบริการ '{service_name}' เรียบร้อยแล้ว", "success")
        return redirect(url_for("admin_services"))

    connection.close()
    return render_template("edit_service.html", service=service)

# ====================================
# เปิดหรือปิดการขายบริการ
# =====================================
@app.route("/admin/services/<int:service_id>/toggle", methods=["POST"])
@admin_required
def toggle_service(service_id):
    connection = get_db_connection()
    service = connection.execute("SELECT service_name, is_active FROM services WHERE service_id = ?", (service_id,)).fetchone()

    if not service:
        connection.close()
        flash("ไม่พบบริการที่ต้องการปรับสถานะ", "error")

        return redirect(url_for("admin_services"))

    new_status = 0 if service["is_active"] == 1 else 1
    connection.execute("UPDATE services SET is_active = ? WHERE service_id = ?", (new_status, service_id))
    connection.commit()
    connection.close()
    status_text = "เปิดให้บริการ" if new_status == 1 else "ปิดให้บริการชั่วคราว"
    flash(f"ปรับสถานะ '{service['service_name']}' เป็น {status_text} แล้ว", "success")

    return redirect(url_for("admin_services"))

# =====================================
# ลบบริการ
# =====================================
@app.route("/admin/services/<int:service_id>/delete", methods=["POST"])
@admin_required
def delete_service(service_id):
    connection = get_db_connection()
    service = connection.execute("SELECT service_name FROM services WHERE service_id = ?", (service_id,)).fetchone()

    if not service:
        connection.close()
        flash("ไม่พบบริการที่ต้องการลบ", "error")
        return redirect(url_for("admin_services"))

    connection.execute("DELETE FROM services WHERE service_id = ?", (service_id,))
    connection.commit()
    connection.close()
    flash(f"ลบบริการ '{service['service_name']}' ออกจากระบบเรียบร้อยแล้ว", "success")
    return redirect(url_for("admin_services"))


# =====================================
# รายชื่อสมาชิก
# =====================================
@app.route("/admin/members")
@admin_required
def admin_members():
    keyword = request.args.get("q", "").strip()
    connection = get_db_connection()
    members = connection.execute("""
        SELECT
            u.user_id,
            u.name,
            u.email,
            u.phone,
            u.created_at,
            COUNT(DISTINCT c.cat_id) AS cat_count,
            COUNT(DISTINCT b.booking_id) AS booking_count,
            COALESCE(SUM(CASE WHEN b.status = 'เสร็จสิ้น' THEN b.price ELSE 0 END), 0) AS total_spent
        FROM users u
        LEFT JOIN cats c ON c.user_id = u.user_id
        LEFT JOIN bookings b ON b.user_id = u.user_id
        WHERE u.role = 'customer'
          AND (
              u.name LIKE ?
              OR u.email LIKE ?
              OR u.phone LIKE ?
          )
        GROUP BY u.user_id, u.name, u.email, u.phone, u.created_at
        ORDER BY u.user_id DESC

    """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")).fetchall()
    connection.close()
    return render_template("admin_members.html", members=members, keyword=keyword)

# =====================================
# รายละเอียดสมาชิกและประวัติการจอง
# =====================================
@app.route("/admin/members/<int:user_id>")
@admin_required
def admin_member_detail(user_id):
    connection = get_db_connection()
    member = connection.execute("""
        SELECT user_id, name, email, phone, created_at
        FROM users
        WHERE user_id = ? AND role = 'customer'
    """, (user_id,)).fetchone()

    if member is None:
        connection.close()
        flash("ไม่พบสมาชิกที่ระบุ", "error")
        return redirect(url_for("admin_members"))

    cats = connection.execute("""
        SELECT cat_id, cat_name, breed, gender, age,
               weight, coat_type, notes, image
        FROM cats
        WHERE user_id = ?
        ORDER BY cat_id DESC

    """, (user_id,)).fetchall()
    bookings = connection.execute("""
        SELECT
            b.booking_id,
            b.service_name,
            b.service_description,
            b.price,
            b.booking_date,
            b.booking_time,
            b.status,
            b.notes,
            b.delivery_type,
            b.delivery_fee,
            b.pickup_address,
            b.latitude,
            b.longitude,
            b.delivery_notes,
            b.distance_km,
            b.payment_method,
            b.payment_status,
            b.payment_slip,
            b.slip_uploaded_at,
            c.cat_name
        FROM bookings b
        LEFT JOIN cats c ON c.cat_id = b.cat_id
        WHERE b.user_id = ?
        ORDER BY b.booking_date DESC, b.booking_time DESC

    """, (user_id,)).fetchall()
    completed_spent = sum(b["price"] for b in bookings if b["status"] == "เสร็จสิ้น")
    connection.close()
    return render_template(
        "admin_member_detail.html",
        member=member,
        cats=cats,
        bookings=bookings,
        completed_spent=completed_spent
    )


# =====================================
# ประวัติการใช้บริการและรายได้
# =====================================
@app.route("/admin/history")
@admin_required
def admin_history():
    keyword = request.args.get("q", "").strip()
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()
    connection = get_db_connection()
    where_clauses = ["b.status = 'เสร็จสิ้น'"]
    params = []

    if keyword:
        where_clauses.append("(u.name LIKE ? OR c.cat_name LIKE ? OR b.service_name LIKE ? OR u.phone LIKE ?)")
        kw = f"%{keyword}%"
        params.extend([kw, kw, kw, kw])

    if date_from:
        where_clauses.append("b.booking_date >= ?")
        params.append(date_from)

    if date_to:
        where_clauses.append("b.booking_date <= ?")
        params.append(date_to)
    history = connection.execute(f"""
        SELECT
            b.booking_id,
            b.booking_date,
            b.booking_time,
            b.service_name,
            b.service_description,
            b.price,
            b.status,
            b.notes,
            b.delivery_type,
            b.delivery_fee,
            b.pickup_address,
            b.latitude,
            b.longitude,
            b.delivery_notes,
            b.distance_km,
            b.payment_method,
            b.payment_status,
            b.payment_slip,
            b.slip_uploaded_at,
            u.name AS customer_name,
            u.phone AS customer_phone,
            c.cat_name,
            c.image AS cat_image
        FROM bookings b
        JOIN users u ON u.user_id = b.user_id
        LEFT JOIN cats c ON c.cat_id = b.cat_id
        WHERE {' AND '.join(where_clauses)}
        ORDER BY b.booking_date DESC, b.booking_time DESC

    """, params).fetchall()
    revenue = sum(item["price"] for item in history)
    avg_price = (revenue / len(history)) if history else 0
    connection.close()
    return render_template(
        "admin_history.html",
        history=history,
        revenue=revenue,
        avg_price=avg_price,
        keyword=keyword,
        date_from=date_from,
        date_to=date_to
    )

# =====================================
# เปลี่ยนสถานะการจองโดย Admin
# =====================================
@app.route(
    "/admin/bookings/<int:booking_id>/status",
    methods=["POST"],
    endpoint="admin_update_booking_status"
)

@admin_required
def admin_update_booking_status(booking_id):
    new_status = request.form.get("status", "").strip()
    allowed_statuses = {
        "รอยืนยัน",
        "ยืนยันแล้ว",
        "ปฏิเสธ",
        "เสร็จสิ้น"
    }

    if new_status not in allowed_statuses:
        flash("สถานะที่เลือกไม่ถูกต้อง", "error")
        return redirect(request.referrer or url_for("admin_bookings"))

    connection = get_db_connection()

    try:
        connection.execute("BEGIN IMMEDIATE")
        booking = connection.execute("""
            SELECT booking_id, booking_date, booking_time, status, service_name, staff_id
            FROM bookings
            WHERE booking_id = ?
        """, (booking_id,)).fetchone()

        if booking is None:
            flash("ไม่พบรายการจอง", "error")
            connection.rollback()
            return redirect(request.referrer or url_for("admin_bookings"))

        # ตรวจสอบเวลาซ้ำหากยืนยันคิว
        if new_status == "ยืนยันแล้ว":
            conflict = connection.execute("""
                SELECT booking_id
                FROM bookings
                WHERE booking_date = ?
                  AND booking_time = ?
                  AND status = 'ยืนยันแล้ว'
                  AND booking_id != ?
                LIMIT 1

            """, (
                booking["booking_date"],
                booking["booking_time"],
                booking_id
            )).fetchone()

            if conflict:
                flash(f"⚠️ เวลานี้มีคิวอื่นได้รับการยืนยันแล้ว (รายการ #{conflict['booking_id']}) กรุณาตรวจสอบก่อน", "warning")
                connection.rollback()
                return redirect(request.referrer or url_for("admin_bookings"))

        # เมื่อสถานะเป็น ปฏิเสธ ยกเลิก หรือ เสร็จสิ้น ให้แจ้งเตือนลูกค้า (notification_read = 0)
        notif_read_status = 0 if new_status in ("ปฏิเสธ", "ยกเลิก", "เสร็จสิ้น") else 1
        connection.execute("""
            UPDATE bookings
            SET status = ?, notification_read = ?
            WHERE booking_id = ?
        """, (new_status, notif_read_status, booking_id))

        # เมื่อบันทึกว่าเสร็จสิ้น และเดิมยังไม่เสร็จสิ้น ให้เพิ่มสถิติจำนวนครั้งที่ให้บริการของพนักงาน
        if new_status == "เสร็จสิ้น" and booking["status"] != "เสร็จสิ้น":
            if booking["staff_id"]:
                connection.execute("""
                    UPDATE staff
                    SET service_count = COALESCE(service_count, 0) + 1
                    WHERE staff_id = ?
                """, (booking["staff_id"],))
        connection.commit()

        if new_status == "ยืนยันแล้ว":
            flash(f"✅ ยืนยันการจองคิว #{booking_id} เรียบร้อยแล้ว", "success")
        elif new_status == "ปฏิเสธ":
            flash(f"✕ ปฏิเสธการจองคิว #{booking_id} เรียบร้อยแล้ว", "warning")
        elif new_status == "เสร็จสิ้น":
            flash(f"✓ บันทึกว่าการจองคิว #{booking_id} ให้บริการเสร็จสิ้นแล้ว (แจ้งเตือนลูกค้าให้ร่วมรีวิวเรียบร้อย)", "success")
        else:
            flash(f"↺ เปลี่ยนสถานะการจองคิว #{booking_id} เป็น 'รอยืนยัน' เรียบร้อยแล้ว", "info")
    except Exception:
        connection.rollback()
        app.logger.exception("เกิดข้อผิดพลาดในการเปลี่ยนสถานะการจอง")
        flash("เกิดข้อผิดพลาดในการบันทึกสถานะ", "error")
    finally:
        connection.close()
    return redirect(request.referrer or url_for("admin_bookings"))

if __name__ == "__main__":
    app.run(debug=True)