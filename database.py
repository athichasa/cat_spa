import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "cat_spa.db")

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db_connection()
    cursor = connection.cursor()

    # ตารางผู้ใช้
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'customer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ตารางข้อมูลแมว
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cats (
            cat_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            cat_name TEXT NOT NULL,
            breed TEXT,
            gender TEXT,
            age INTEGER,
            weight REAL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # เพิ่มคอลัมน์ coat_type
    columns = [
        row["name"]
            for row in connection.execute(
                "PRAGMA table_info(cats)"
            ).fetchall()
    ]

    if "coat_type" not in columns:
        connection.execute(
            "ALTER TABLE cats ADD COLUMN coat_type TEXT"
        )

    #ตารางเก็บภาพน้องแมวของผู้ใช้
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CATS (
        cat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        cat_name TEXT NOT NULL,
        breed TEXT,
        gender TEXT,
        age INTEGER,
        weight REAL,
        notes TEXT,
        image TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # เพิ่มคอลัมน์ image
    columns = [
        row["name"]
        for row in connection.execute("PRAGMA table_info(cats)").fetchall()
    ]

    if "image" not in columns:
        connection.execute("ALTER TABLE cats ADD COLUMN image TEXT")

    
    # เพิ่มคอลัมน์หลักฐานการยินยอมให้ฐานข้อมูลเดิม
    columns = [
        row["name"]
        for row in connection.execute(
            "PRAGMA table_info(users)"
        ).fetchall()
    ]

    new_columns = {
        "terms_accepted_at": "TEXT",
        "terms_version": "TEXT",
        "privacy_acknowledged_at": "TEXT",
        "privacy_version": "TEXT",
    }

    for column_name, column_type in new_columns.items():
        if column_name not in columns:
            connection.execute(
                f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
            )

    # ตารางข้อมูลการจอง
    connection.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            cat_id INTEGER NOT NULL,
            service_name TEXT NOT NULL,
            price INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            booking_time TEXT NOT NULL,
            notes TEXT,
            status TEXT NOT NULL DEFAULT 'รอยืนยัน',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    
    # เพิ่มคอลัมน์รายละเอียดแพ็กเกจ
    booking_columns = [
        row["name"]
        for row in connection.execute(
            "PRAGMA table_info(bookings)"
        ).fetchall()
    ]

    if "service_description" not in booking_columns:
        connection.execute("""
            ALTER TABLE bookings
            ADD COLUMN service_description TEXT
        """)

    # เพิ่มคอลัมน์ระบบบริการรับ-ส่งน้องแมว (Pet Taxi / Delivery Service)
    delivery_columns = {
        "delivery_type": "TEXT DEFAULT 'none'",
        "delivery_fee": "REAL DEFAULT 0",
        "pickup_address": "TEXT DEFAULT ''",
        "latitude": "REAL DEFAULT NULL",
        "longitude": "REAL DEFAULT NULL",
        "delivery_notes": "TEXT DEFAULT ''",
        "distance_km": "REAL DEFAULT 0",
        "payment_method": "TEXT DEFAULT 'pay_at_shop'",
        "payment_status": "TEXT DEFAULT 'รอชำระหน้าร้าน'",
        "payment_slip": "TEXT DEFAULT ''",
        "slip_uploaded_at": "TEXT DEFAULT ''",
        "notification_read": "INTEGER DEFAULT 0",
        "staff_id": "INTEGER DEFAULT NULL",
        "staff_name": "TEXT DEFAULT ''",
        "has_reviewed": "INTEGER DEFAULT 0"
    }
    for col_name, col_type in delivery_columns.items():
        if col_name not in booking_columns:
            connection.execute(f"ALTER TABLE bookings ADD COLUMN {col_name} {col_type}")

    # ตารางบริการและแพ็กเกจ
    connection.execute("""
        CREATE TABLE IF NOT EXISTS services (
            service_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            service_name TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL CHECK(price >= 0),
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # เพิ่มแพ็กเกจตัวอย่างเฉพาะเมื่อยังไม่มีข้อมูล
    service_count = connection.execute(
        "SELECT COUNT(*) FROM services"
    ).fetchone()[0]

    default_services = [
        (
            "อาบน้ำแมว",
            "อาบน้ำแมวขนสั้น",
            "อาบน้ำ ล้างแชมพู เช็ดตัว และเป่าขนให้แห้ง",
            300
        ),
        (
            "อาบน้ำแมว",
            "อาบน้ำแมวขนกึ่งยาว",
            "อาบน้ำ ทำความสะอาด และเป่าขนพร้อมหวีสางขน",
            400
        ),
        (
            "อาบน้ำแมว",
            "อาบน้ำแมวขนยาว",
            "อาบน้ำ เป่าขน และหวีขนให้เรียบร้อย",
            500
        ),
        (
            "อาบน้ำแมว",
            "อาบน้ำพร้อมหวีสางขนพันกัน",
            "สำหรับแมวที่มีขนพันกันเล็กน้อย ใช้เวลาเพิ่มตามสภาพขน",
            600
        ),
        (
            "สปาแมว",
            "สปาบำรุงขน",
            "อาบน้ำและใช้ผลิตภัณฑ์บำรุงขนสำหรับแมว",
            450
        ),
        (
            "สปาแมว",
            "สปาขนนุ่ม",
            "อาบน้ำ บำรุงขน และหวีขนให้เรียบร้อย",
            550
        ),
        (
            "สปาแมว",
            "สปาดูแลผิวหนัง",
            "ทำความสะอาดและเลือกผลิตภัณฑ์ดูแลผิวที่เหมาะสม",
            650
        ),
        (
            "สปาแมว",
            "สปาบำรุงขนพร้อมหวีสาง",
            "อาบน้ำ บำรุงขน เป่าขน และหวีสางขนพันกันเล็กน้อย",
            700
        ),
        (
            "ตัดแต่งขน",
            "เล็มขนเฉพาะจุด",
            "เล็มขนบริเวณก้นหรือจุดที่จำเป็นตามความเหมาะสม",
            200
        ),
        (
            "ตัดแต่งขน",
            "ตัดแต่งทรงพื้นฐาน",
            "เล็มและจัดทรงขนให้เรียบร้อย",
            400
        ),
        (
            "ตัดแต่งขน",
            "ตัดทรงสิงโต",
            "ตัดขนลำตัวให้สั้นและคงขนบริเวณศีรษะตามรูปแบบทรง",
            600
        ),
        (
            "ตัดแต่งขน",
            "ตัดแต่งขนทั่วตัวแบบละเอียด",
            "ตัดแต่งขนทั่วตัวและเก็บรายละเอียดตามทรงที่ตกลงกัน",
            700
        ),
        (
            "ตัดเล็บ",
            "ตัดเล็บอย่างเดียว",
            "ตัดปลายเล็บอย่างระมัดระวัง",
            100
        ),
        (
            "ตัดเล็บ",
            "ตัดเล็บพร้อมตรวจอุ้งเท้า",
            "ตัดเล็บและตรวจดูความเรียบร้อยของอุ้งเท้าเบื้องต้น",
            150
        ),
        (
            "ตัดเล็บ",
            "ตัดเล็บพร้อมเล็มขนอุ้งเท้า",
            "ตัดเล็บและเล็มขนบริเวณอุ้งเท้าตามความเหมาะสม",
            200
        )
    ]

    for cat, sname, sdesc, sprice in default_services:
        row = connection.execute(
            "SELECT service_id FROM services WHERE service_name = ?", (sname,)
        ).fetchone()
        if not row:
            connection.execute("""
                INSERT INTO services
                    (category, service_name, description, price, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, (cat, sname, sdesc, sprice))
        else:
            connection.execute("""
                UPDATE services
                SET description = ?, price = ?
                WHERE service_name = ?
            """, (sdesc, sprice, sname))

    # ตารางพนักงาน (Groomer / Staff)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            nickname TEXT NOT NULL,
            image TEXT NOT NULL,
            role_title TEXT NOT NULL,
            specialties TEXT NOT NULL,
            work_days TEXT NOT NULL,
            work_hours TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            status_text TEXT DEFAULT 'พร้อมให้บริการ',
            experience_years INTEGER DEFAULT 3,
            highlights TEXT NOT NULL,
            service_count INTEGER DEFAULT 0,
            rating REAL DEFAULT 5.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ตารางรีวิวและความคิดเห็น (Reviews)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER UNIQUE,
            user_id INTEGER,
            user_name TEXT NOT NULL,
            cat_name TEXT,
            staff_id INTEGER,
            staff_name TEXT,
            service_name TEXT,
            shop_rating INTEGER NOT NULL CHECK(shop_rating BETWEEN 1 AND 5),
            shop_comment TEXT,
            staff_rating INTEGER NOT NULL CHECK(staff_rating BETWEEN 1 AND 5),
            staff_comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (staff_id) REFERENCES staff(staff_id)
        )
    """)

    # เพิ่มข้อมูลพนักงานเริ่มต้น 3 คน หากยังไม่มีข้อมูล
    staff_count = connection.execute("SELECT COUNT(*) FROM staff").fetchone()[0]
    if staff_count == 0:
        default_staff = [
            (
                1,
                "กัญญาพัชร มั่นคง (ต้นเตย)",
                "ต้นเตย",
                "Service Staff 1.png",
                "Senior Cat Spa & Aromatherapy Specialist",
                "สปาอโรม่าบำบัดกลิ่นคลาสสิก, วารีบำบัดขนนุ่ม, นวดผ่อนคลายกล้ามเนื้อคลายเครียด, สปาดีท็อกซ์ผิวหนังแพ้ง่าย",
                "อังคาร - เสาร์",
                "09:00 - 18:00 น.",
                1,
                "พร้อมให้บริการ",
                4,
                "สัมผัสมือเบามาก นวดสปาเก่ง น้องแมวจะเคลิ้มหลับสบาย ไม่เครียดแม้แมวที่ขี้ตื่นตกใจง่าย",
                142,
                4.9
            ),
            (
                2,
                "พิมลดา สุวรรณเวช (มีมี่)",
                "มีมี่",
                "Service Staff 2.png",
                "Senior Feline Groomer & Haircut Stylist",
                "ตัดแต่งทรงขนแมวขนยาว (Persian, Ragdoll, Maine Coon), ตัดทรงสิงโต, สางสังกะตังอย่างปราณีตไม่เจ็บผิว",
                "จันทร์ - ศุกร์",
                "10:00 - 19:00 น.",
                1,
                "พร้อมให้บริการ",
                5,
                "ตัดแต่งทรงขนเนี๊ยบสวยสไตล์เกาหลี ใจเย็นขั้นสุด สื่อสารและอ่านภาษาทางกายน้องแมวออกอย่างแม่นยำ ปลอบประโลมน้องเก่ง",
                186,
                5.0
            ),
            (
                3,
                "ณิชากานต์ พลอยประเสริฐ (อุ๋มอิ๋ม)",
                "อุ๋มอิ๋ม",
                "Service Staff 3.png",
                "Cat Hygiene Specialist & Feline Behaviorist",
                "อาบน้ำทำความสะอาดล้ำลึก, ตัดเล็บมือเบา, เช็ดหูและคราบน้ำตา, เชี่ยวชาญพิเศษในการรับมือแมวขี้ระแวงหรือดื้อเป็นพิเศษ",
                "พุธ - อาทิตย์",
                "09:30 - 18:30 น.",
                1,
                "พร้อมให้บริการ",
                3,
                "จับน้องแมวอย่างทะนุถนอม ไม่ใช้ความรุนแรง มีเทคนิคเบี่ยงเบนความสนใจ แมวไม่เคยงอแงขณะตัดเล็บและเช็ดหู",
                115,
                4.8
            )
        ]
        connection.executemany("""
            INSERT INTO staff (
                staff_id, name, nickname, image, role_title, specialties,
                work_days, work_hours, is_active, status_text, experience_years,
                highlights, service_count, rating
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, default_staff)

    connection.commit()
    connection.close()