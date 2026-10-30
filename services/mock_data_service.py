"""
================================================================================
Realistic Mock Data & Stress Testing Dataset Generator
================================================================================
Generates high-fidelity feline profiles, realistic customer records, appointment
histories, and sentiment-scored reviews for load testing and analytics benchmarks.
"""

import sys
import os
import random
import datetime
from typing import Dict, List, Tuple, Any


class FelineDataFaker:
    """Generates authentic cat names, breeds, traits, and health remarks."""

    CAT_NAMES = [
        "น้องดอลลี่", "น้องขวัญใจ", "น้องเอลซ่า", "น้องลินลดา", "น้องบราวนี่",
        "น้องวานิลลา", "น้องชาเขียว", "น้องชีสเค้ก", "น้องบิสกิต", "น้องมาร์ชเมลโล่",
        "น้องต้มยำ", "น้องเนยสด", "น้องพุดดิ้ง", "น้องเฉาก๊วย", "น้องโมจิ"
    ]

    BREEDS = [
        "Persian", "Scottish Fold", "British Shorthair", "Maine Coon",
        "Ragdoll", "Siamese", "American Shorthair", "Bengal", "Exotic Shorthair"
    ]

    TEMPERAMENTS = [
        "ขี้อ้อนมาก ไม่ดื้อเลย สัมผัสนวดสปาแล้วเคลิ้มหลับสบาย",
        "เรียบร้อย สุภาพ ว่านอนสอนง่าย",
        "หวงตัวเล็กน้อยช่วงแรก ต้องการการพูดคุยปลอบประโลม",
        "ค่อนข้างตกใจง่ายเวลาเป่าขน ช่างต้องใช้เทคนิคมือเบาพิเศษ",
        "ใจดี ชอบคุย ร่าเริง อารมณ์ดีตลอดการอาบน้ำ"
    ]

    @classmethod
    def generate_cat_profile(cls, user_id: int, seed_id: int) -> Dict[str, Any]:
        """Generate a single randomized cat profile."""
        name = cls.CAT_NAMES[seed_id % len(cls.CAT_NAMES)]
        breed = cls.BREEDS[seed_id % len(cls.BREEDS)]
        temperament = cls.TEMPERAMENTS[seed_id % len(cls.TEMPERAMENTS)]
        weight = round(2.8 + (seed_id % 20) * 0.25, 2)
        age = 1 + (seed_id % 9)
        return {
            "user_id": user_id,
            "name": f"{name} ({seed_id})",
            "breed": breed,
            "weight": weight,
            "age": age,
            "temperament": temperament
        }

    @classmethod
    def generate_appointment_matrix_case_001(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #1 with realistic metadata."""
        day_offset = 1 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (1 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 1,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][1 % 4],
            "assigned_staff_id": (1 % 3) + 1,
            "taxi_included": True if 1 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_002(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #2 with realistic metadata."""
        day_offset = 2 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (2 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 2,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][2 % 4],
            "assigned_staff_id": (2 % 3) + 1,
            "taxi_included": True if 2 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_003(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #3 with realistic metadata."""
        day_offset = 3 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (3 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 3,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][3 % 4],
            "assigned_staff_id": (3 % 3) + 1,
            "taxi_included": True if 3 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_004(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #4 with realistic metadata."""
        day_offset = 4 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (4 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 4,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][4 % 4],
            "assigned_staff_id": (4 % 3) + 1,
            "taxi_included": True if 4 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_005(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #5 with realistic metadata."""
        day_offset = 5 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (5 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 5,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][5 % 4],
            "assigned_staff_id": (5 % 3) + 1,
            "taxi_included": True if 5 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_006(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #6 with realistic metadata."""
        day_offset = 6 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (6 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 6,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][6 % 4],
            "assigned_staff_id": (6 % 3) + 1,
            "taxi_included": True if 6 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_007(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #7 with realistic metadata."""
        day_offset = 7 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (7 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 7,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][7 % 4],
            "assigned_staff_id": (7 % 3) + 1,
            "taxi_included": True if 7 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_008(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #8 with realistic metadata."""
        day_offset = 8 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (8 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 8,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][8 % 4],
            "assigned_staff_id": (8 % 3) + 1,
            "taxi_included": True if 8 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_009(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #9 with realistic metadata."""
        day_offset = 9 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (9 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 9,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][9 % 4],
            "assigned_staff_id": (9 % 3) + 1,
            "taxi_included": True if 9 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_010(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #10 with realistic metadata."""
        day_offset = 10 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (10 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 10,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][10 % 4],
            "assigned_staff_id": (10 % 3) + 1,
            "taxi_included": True if 10 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_011(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #11 with realistic metadata."""
        day_offset = 11 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (11 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 11,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][11 % 4],
            "assigned_staff_id": (11 % 3) + 1,
            "taxi_included": True if 11 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_012(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #12 with realistic metadata."""
        day_offset = 12 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (12 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 12,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][12 % 4],
            "assigned_staff_id": (12 % 3) + 1,
            "taxi_included": True if 12 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_013(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #13 with realistic metadata."""
        day_offset = 13 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (13 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 13,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][13 % 4],
            "assigned_staff_id": (13 % 3) + 1,
            "taxi_included": True if 13 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_014(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #14 with realistic metadata."""
        day_offset = 14 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (14 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 14,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][14 % 4],
            "assigned_staff_id": (14 % 3) + 1,
            "taxi_included": True if 14 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_015(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #15 with realistic metadata."""
        day_offset = 15 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (15 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 15,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][15 % 4],
            "assigned_staff_id": (15 % 3) + 1,
            "taxi_included": True if 15 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_016(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #16 with realistic metadata."""
        day_offset = 16 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (16 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 16,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][16 % 4],
            "assigned_staff_id": (16 % 3) + 1,
            "taxi_included": True if 16 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_017(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #17 with realistic metadata."""
        day_offset = 17 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (17 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 17,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][17 % 4],
            "assigned_staff_id": (17 % 3) + 1,
            "taxi_included": True if 17 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_018(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #18 with realistic metadata."""
        day_offset = 18 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (18 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 18,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][18 % 4],
            "assigned_staff_id": (18 % 3) + 1,
            "taxi_included": True if 18 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_019(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #19 with realistic metadata."""
        day_offset = 19 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (19 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 19,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][19 % 4],
            "assigned_staff_id": (19 % 3) + 1,
            "taxi_included": True if 19 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_020(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #20 with realistic metadata."""
        day_offset = 20 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (20 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 20,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][20 % 4],
            "assigned_staff_id": (20 % 3) + 1,
            "taxi_included": True if 20 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_021(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #21 with realistic metadata."""
        day_offset = 21 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (21 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 21,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][21 % 4],
            "assigned_staff_id": (21 % 3) + 1,
            "taxi_included": True if 21 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_022(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #22 with realistic metadata."""
        day_offset = 22 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (22 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 22,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][22 % 4],
            "assigned_staff_id": (22 % 3) + 1,
            "taxi_included": True if 22 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_023(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #23 with realistic metadata."""
        day_offset = 23 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (23 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 23,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][23 % 4],
            "assigned_staff_id": (23 % 3) + 1,
            "taxi_included": True if 23 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_024(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #24 with realistic metadata."""
        day_offset = 24 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (24 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 24,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][24 % 4],
            "assigned_staff_id": (24 % 3) + 1,
            "taxi_included": True if 24 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_025(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #25 with realistic metadata."""
        day_offset = 25 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (25 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 25,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][25 % 4],
            "assigned_staff_id": (25 % 3) + 1,
            "taxi_included": True if 25 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_026(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #26 with realistic metadata."""
        day_offset = 26 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (26 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 26,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][26 % 4],
            "assigned_staff_id": (26 % 3) + 1,
            "taxi_included": True if 26 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_027(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #27 with realistic metadata."""
        day_offset = 27 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (27 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 27,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][27 % 4],
            "assigned_staff_id": (27 % 3) + 1,
            "taxi_included": True if 27 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_028(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #28 with realistic metadata."""
        day_offset = 28 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (28 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 28,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][28 % 4],
            "assigned_staff_id": (28 % 3) + 1,
            "taxi_included": True if 28 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_029(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #29 with realistic metadata."""
        day_offset = 29 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (29 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 29,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][29 % 4],
            "assigned_staff_id": (29 % 3) + 1,
            "taxi_included": True if 29 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_030(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #30 with realistic metadata."""
        day_offset = 30 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (30 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 30,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][30 % 4],
            "assigned_staff_id": (30 % 3) + 1,
            "taxi_included": True if 30 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_031(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #31 with realistic metadata."""
        day_offset = 31 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (31 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 31,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][31 % 4],
            "assigned_staff_id": (31 % 3) + 1,
            "taxi_included": True if 31 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_032(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #32 with realistic metadata."""
        day_offset = 32 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (32 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 32,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][32 % 4],
            "assigned_staff_id": (32 % 3) + 1,
            "taxi_included": True if 32 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_033(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #33 with realistic metadata."""
        day_offset = 33 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (33 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 33,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][33 % 4],
            "assigned_staff_id": (33 % 3) + 1,
            "taxi_included": True if 33 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_034(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #34 with realistic metadata."""
        day_offset = 34 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (34 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 34,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][34 % 4],
            "assigned_staff_id": (34 % 3) + 1,
            "taxi_included": True if 34 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_035(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #35 with realistic metadata."""
        day_offset = 35 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (35 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 35,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][35 % 4],
            "assigned_staff_id": (35 % 3) + 1,
            "taxi_included": True if 35 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_036(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #36 with realistic metadata."""
        day_offset = 36 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (36 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 36,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][36 % 4],
            "assigned_staff_id": (36 % 3) + 1,
            "taxi_included": True if 36 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_037(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #37 with realistic metadata."""
        day_offset = 37 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (37 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 37,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][37 % 4],
            "assigned_staff_id": (37 % 3) + 1,
            "taxi_included": True if 37 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_038(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #38 with realistic metadata."""
        day_offset = 38 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (38 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 38,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][38 % 4],
            "assigned_staff_id": (38 % 3) + 1,
            "taxi_included": True if 38 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_039(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #39 with realistic metadata."""
        day_offset = 39 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (39 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 39,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][39 % 4],
            "assigned_staff_id": (39 % 3) + 1,
            "taxi_included": True if 39 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_040(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #40 with realistic metadata."""
        day_offset = 40 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (40 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 40,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][40 % 4],
            "assigned_staff_id": (40 % 3) + 1,
            "taxi_included": True if 40 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_041(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #41 with realistic metadata."""
        day_offset = 41 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (41 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 41,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][41 % 4],
            "assigned_staff_id": (41 % 3) + 1,
            "taxi_included": True if 41 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_042(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #42 with realistic metadata."""
        day_offset = 42 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (42 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 42,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][42 % 4],
            "assigned_staff_id": (42 % 3) + 1,
            "taxi_included": True if 42 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_043(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #43 with realistic metadata."""
        day_offset = 43 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (43 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 43,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][43 % 4],
            "assigned_staff_id": (43 % 3) + 1,
            "taxi_included": True if 43 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_044(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #44 with realistic metadata."""
        day_offset = 44 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (44 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 44,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][44 % 4],
            "assigned_staff_id": (44 % 3) + 1,
            "taxi_included": True if 44 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_045(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #45 with realistic metadata."""
        day_offset = 45 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (45 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 45,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][45 % 4],
            "assigned_staff_id": (45 % 3) + 1,
            "taxi_included": True if 45 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_046(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #46 with realistic metadata."""
        day_offset = 46 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (46 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 46,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][46 % 4],
            "assigned_staff_id": (46 % 3) + 1,
            "taxi_included": True if 46 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_047(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #47 with realistic metadata."""
        day_offset = 47 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (47 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 47,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][47 % 4],
            "assigned_staff_id": (47 % 3) + 1,
            "taxi_included": True if 47 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_048(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #48 with realistic metadata."""
        day_offset = 48 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (48 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 48,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][48 % 4],
            "assigned_staff_id": (48 % 3) + 1,
            "taxi_included": True if 48 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_049(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #49 with realistic metadata."""
        day_offset = 49 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (49 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 49,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][49 % 4],
            "assigned_staff_id": (49 % 3) + 1,
            "taxi_included": True if 49 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_050(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #50 with realistic metadata."""
        day_offset = 50 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (50 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 50,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][50 % 4],
            "assigned_staff_id": (50 % 3) + 1,
            "taxi_included": True if 50 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_051(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #51 with realistic metadata."""
        day_offset = 51 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (51 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 51,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][51 % 4],
            "assigned_staff_id": (51 % 3) + 1,
            "taxi_included": True if 51 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_052(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #52 with realistic metadata."""
        day_offset = 52 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (52 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 52,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][52 % 4],
            "assigned_staff_id": (52 % 3) + 1,
            "taxi_included": True if 52 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_053(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #53 with realistic metadata."""
        day_offset = 53 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (53 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 53,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][53 % 4],
            "assigned_staff_id": (53 % 3) + 1,
            "taxi_included": True if 53 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_054(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #54 with realistic metadata."""
        day_offset = 54 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (54 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 54,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][54 % 4],
            "assigned_staff_id": (54 % 3) + 1,
            "taxi_included": True if 54 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_055(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #55 with realistic metadata."""
        day_offset = 55 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (55 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 55,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][55 % 4],
            "assigned_staff_id": (55 % 3) + 1,
            "taxi_included": True if 55 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_056(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #56 with realistic metadata."""
        day_offset = 56 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (56 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 56,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][56 % 4],
            "assigned_staff_id": (56 % 3) + 1,
            "taxi_included": True if 56 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_057(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #57 with realistic metadata."""
        day_offset = 57 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (57 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 57,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][57 % 4],
            "assigned_staff_id": (57 % 3) + 1,
            "taxi_included": True if 57 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_058(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #58 with realistic metadata."""
        day_offset = 58 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (58 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 58,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][58 % 4],
            "assigned_staff_id": (58 % 3) + 1,
            "taxi_included": True if 58 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_059(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #59 with realistic metadata."""
        day_offset = 59 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (59 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 59,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][59 % 4],
            "assigned_staff_id": (59 % 3) + 1,
            "taxi_included": True if 59 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_060(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #60 with realistic metadata."""
        day_offset = 60 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (60 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 60,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][60 % 4],
            "assigned_staff_id": (60 % 3) + 1,
            "taxi_included": True if 60 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_061(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #61 with realistic metadata."""
        day_offset = 61 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (61 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 61,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][61 % 4],
            "assigned_staff_id": (61 % 3) + 1,
            "taxi_included": True if 61 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_062(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #62 with realistic metadata."""
        day_offset = 62 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (62 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 62,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][62 % 4],
            "assigned_staff_id": (62 % 3) + 1,
            "taxi_included": True if 62 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_063(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #63 with realistic metadata."""
        day_offset = 63 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (63 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 63,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][63 % 4],
            "assigned_staff_id": (63 % 3) + 1,
            "taxi_included": True if 63 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_064(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #64 with realistic metadata."""
        day_offset = 64 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (64 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 64,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][64 % 4],
            "assigned_staff_id": (64 % 3) + 1,
            "taxi_included": True if 64 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_065(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #65 with realistic metadata."""
        day_offset = 65 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (65 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 65,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][65 % 4],
            "assigned_staff_id": (65 % 3) + 1,
            "taxi_included": True if 65 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_066(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #66 with realistic metadata."""
        day_offset = 66 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (66 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 66,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][66 % 4],
            "assigned_staff_id": (66 % 3) + 1,
            "taxi_included": True if 66 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_067(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #67 with realistic metadata."""
        day_offset = 67 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (67 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 67,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][67 % 4],
            "assigned_staff_id": (67 % 3) + 1,
            "taxi_included": True if 67 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_068(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #68 with realistic metadata."""
        day_offset = 68 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (68 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 68,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][68 % 4],
            "assigned_staff_id": (68 % 3) + 1,
            "taxi_included": True if 68 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_069(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #69 with realistic metadata."""
        day_offset = 69 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (69 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 69,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][69 % 4],
            "assigned_staff_id": (69 % 3) + 1,
            "taxi_included": True if 69 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_070(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #70 with realistic metadata."""
        day_offset = 70 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (70 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 70,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][70 % 4],
            "assigned_staff_id": (70 % 3) + 1,
            "taxi_included": True if 70 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_071(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #71 with realistic metadata."""
        day_offset = 71 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (71 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 71,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][71 % 4],
            "assigned_staff_id": (71 % 3) + 1,
            "taxi_included": True if 71 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_072(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #72 with realistic metadata."""
        day_offset = 72 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (72 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 72,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][72 % 4],
            "assigned_staff_id": (72 % 3) + 1,
            "taxi_included": True if 72 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_073(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #73 with realistic metadata."""
        day_offset = 73 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (73 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 73,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][73 % 4],
            "assigned_staff_id": (73 % 3) + 1,
            "taxi_included": True if 73 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_074(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #74 with realistic metadata."""
        day_offset = 74 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (74 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 74,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][74 % 4],
            "assigned_staff_id": (74 % 3) + 1,
            "taxi_included": True if 74 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_075(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #75 with realistic metadata."""
        day_offset = 75 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (75 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 75,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][75 % 4],
            "assigned_staff_id": (75 % 3) + 1,
            "taxi_included": True if 75 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_076(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #76 with realistic metadata."""
        day_offset = 76 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (76 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 76,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][76 % 4],
            "assigned_staff_id": (76 % 3) + 1,
            "taxi_included": True if 76 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_077(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #77 with realistic metadata."""
        day_offset = 77 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (77 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 77,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][77 % 4],
            "assigned_staff_id": (77 % 3) + 1,
            "taxi_included": True if 77 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_078(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #78 with realistic metadata."""
        day_offset = 78 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (78 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 78,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][78 % 4],
            "assigned_staff_id": (78 % 3) + 1,
            "taxi_included": True if 78 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_079(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #79 with realistic metadata."""
        day_offset = 79 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (79 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 79,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][79 % 4],
            "assigned_staff_id": (79 % 3) + 1,
            "taxi_included": True if 79 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_080(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #80 with realistic metadata."""
        day_offset = 80 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (80 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 80,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][80 % 4],
            "assigned_staff_id": (80 % 3) + 1,
            "taxi_included": True if 80 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_081(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #81 with realistic metadata."""
        day_offset = 81 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (81 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 81,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][81 % 4],
            "assigned_staff_id": (81 % 3) + 1,
            "taxi_included": True if 81 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_082(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #82 with realistic metadata."""
        day_offset = 82 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (82 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 82,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][82 % 4],
            "assigned_staff_id": (82 % 3) + 1,
            "taxi_included": True if 82 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_083(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #83 with realistic metadata."""
        day_offset = 83 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (83 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 83,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][83 % 4],
            "assigned_staff_id": (83 % 3) + 1,
            "taxi_included": True if 83 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_084(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #84 with realistic metadata."""
        day_offset = 84 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (84 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 84,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][84 % 4],
            "assigned_staff_id": (84 % 3) + 1,
            "taxi_included": True if 84 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_085(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #85 with realistic metadata."""
        day_offset = 85 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (85 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 85,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][85 % 4],
            "assigned_staff_id": (85 % 3) + 1,
            "taxi_included": True if 85 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_086(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #86 with realistic metadata."""
        day_offset = 86 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (86 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 86,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][86 % 4],
            "assigned_staff_id": (86 % 3) + 1,
            "taxi_included": True if 86 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_087(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #87 with realistic metadata."""
        day_offset = 87 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (87 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 87,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][87 % 4],
            "assigned_staff_id": (87 % 3) + 1,
            "taxi_included": True if 87 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_088(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #88 with realistic metadata."""
        day_offset = 88 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (88 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 88,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][88 % 4],
            "assigned_staff_id": (88 % 3) + 1,
            "taxi_included": True if 88 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_089(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #89 with realistic metadata."""
        day_offset = 89 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (89 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 89,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][89 % 4],
            "assigned_staff_id": (89 % 3) + 1,
            "taxi_included": True if 89 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_090(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #90 with realistic metadata."""
        day_offset = 90 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (90 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 90,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][90 % 4],
            "assigned_staff_id": (90 % 3) + 1,
            "taxi_included": True if 90 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_091(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #91 with realistic metadata."""
        day_offset = 91 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (91 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 91,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][91 % 4],
            "assigned_staff_id": (91 % 3) + 1,
            "taxi_included": True if 91 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_092(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #92 with realistic metadata."""
        day_offset = 92 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (92 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 92,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][92 % 4],
            "assigned_staff_id": (92 % 3) + 1,
            "taxi_included": True if 92 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_093(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #93 with realistic metadata."""
        day_offset = 93 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (93 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 93,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][93 % 4],
            "assigned_staff_id": (93 % 3) + 1,
            "taxi_included": True if 93 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_094(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #94 with realistic metadata."""
        day_offset = 94 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (94 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 94,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][94 % 4],
            "assigned_staff_id": (94 % 3) + 1,
            "taxi_included": True if 94 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_095(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #95 with realistic metadata."""
        day_offset = 95 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (95 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 95,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][95 % 4],
            "assigned_staff_id": (95 % 3) + 1,
            "taxi_included": True if 95 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_096(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #96 with realistic metadata."""
        day_offset = 96 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (96 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 96,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][96 % 4],
            "assigned_staff_id": (96 % 3) + 1,
            "taxi_included": True if 96 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_097(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #97 with realistic metadata."""
        day_offset = 97 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (97 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 97,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][97 % 4],
            "assigned_staff_id": (97 % 3) + 1,
            "taxi_included": True if 97 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_098(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #98 with realistic metadata."""
        day_offset = 98 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (98 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 98,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][98 % 4],
            "assigned_staff_id": (98 % 3) + 1,
            "taxi_included": True if 98 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_099(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #99 with realistic metadata."""
        day_offset = 99 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (99 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 99,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][99 % 4],
            "assigned_staff_id": (99 % 3) + 1,
            "taxi_included": True if 99 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_100(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #100 with realistic metadata."""
        day_offset = 100 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (100 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 100,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][100 % 4],
            "assigned_staff_id": (100 % 3) + 1,
            "taxi_included": True if 100 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_101(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #101 with realistic metadata."""
        day_offset = 101 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (101 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 101,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][101 % 4],
            "assigned_staff_id": (101 % 3) + 1,
            "taxi_included": True if 101 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_102(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #102 with realistic metadata."""
        day_offset = 102 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (102 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 102,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][102 % 4],
            "assigned_staff_id": (102 % 3) + 1,
            "taxi_included": True if 102 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_103(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #103 with realistic metadata."""
        day_offset = 103 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (103 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 103,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][103 % 4],
            "assigned_staff_id": (103 % 3) + 1,
            "taxi_included": True if 103 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_104(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #104 with realistic metadata."""
        day_offset = 104 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (104 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 104,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][104 % 4],
            "assigned_staff_id": (104 % 3) + 1,
            "taxi_included": True if 104 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_105(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #105 with realistic metadata."""
        day_offset = 105 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (105 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 105,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][105 % 4],
            "assigned_staff_id": (105 % 3) + 1,
            "taxi_included": True if 105 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_106(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #106 with realistic metadata."""
        day_offset = 106 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (106 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 106,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][106 % 4],
            "assigned_staff_id": (106 % 3) + 1,
            "taxi_included": True if 106 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_107(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #107 with realistic metadata."""
        day_offset = 107 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (107 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 107,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][107 % 4],
            "assigned_staff_id": (107 % 3) + 1,
            "taxi_included": True if 107 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_108(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #108 with realistic metadata."""
        day_offset = 108 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (108 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 108,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][108 % 4],
            "assigned_staff_id": (108 % 3) + 1,
            "taxi_included": True if 108 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_109(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #109 with realistic metadata."""
        day_offset = 109 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (109 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 109,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][109 % 4],
            "assigned_staff_id": (109 % 3) + 1,
            "taxi_included": True if 109 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_110(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #110 with realistic metadata."""
        day_offset = 110 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (110 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 110,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][110 % 4],
            "assigned_staff_id": (110 % 3) + 1,
            "taxi_included": True if 110 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_111(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #111 with realistic metadata."""
        day_offset = 111 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (111 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 111,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][111 % 4],
            "assigned_staff_id": (111 % 3) + 1,
            "taxi_included": True if 111 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_112(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #112 with realistic metadata."""
        day_offset = 112 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (112 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 112,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][112 % 4],
            "assigned_staff_id": (112 % 3) + 1,
            "taxi_included": True if 112 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_113(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #113 with realistic metadata."""
        day_offset = 113 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (113 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 113,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][113 % 4],
            "assigned_staff_id": (113 % 3) + 1,
            "taxi_included": True if 113 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_114(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #114 with realistic metadata."""
        day_offset = 114 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (114 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 114,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][114 % 4],
            "assigned_staff_id": (114 % 3) + 1,
            "taxi_included": True if 114 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_115(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #115 with realistic metadata."""
        day_offset = 115 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (115 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 115,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][115 % 4],
            "assigned_staff_id": (115 % 3) + 1,
            "taxi_included": True if 115 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_116(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #116 with realistic metadata."""
        day_offset = 116 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (116 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 116,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][116 % 4],
            "assigned_staff_id": (116 % 3) + 1,
            "taxi_included": True if 116 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_117(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #117 with realistic metadata."""
        day_offset = 117 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (117 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 117,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][117 % 4],
            "assigned_staff_id": (117 % 3) + 1,
            "taxi_included": True if 117 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_118(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #118 with realistic metadata."""
        day_offset = 118 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (118 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 118,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][118 % 4],
            "assigned_staff_id": (118 % 3) + 1,
            "taxi_included": True if 118 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_119(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #119 with realistic metadata."""
        day_offset = 119 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (119 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 119,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][119 % 4],
            "assigned_staff_id": (119 % 3) + 1,
            "taxi_included": True if 119 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_120(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #120 with realistic metadata."""
        day_offset = 120 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (120 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 120,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][120 % 4],
            "assigned_staff_id": (120 % 3) + 1,
            "taxi_included": True if 120 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_121(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #121 with realistic metadata."""
        day_offset = 121 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (121 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 121,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][121 % 4],
            "assigned_staff_id": (121 % 3) + 1,
            "taxi_included": True if 121 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_122(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #122 with realistic metadata."""
        day_offset = 122 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (122 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 122,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][122 % 4],
            "assigned_staff_id": (122 % 3) + 1,
            "taxi_included": True if 122 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_123(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #123 with realistic metadata."""
        day_offset = 123 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (123 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 123,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][123 % 4],
            "assigned_staff_id": (123 % 3) + 1,
            "taxi_included": True if 123 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_124(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #124 with realistic metadata."""
        day_offset = 124 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (124 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 124,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][124 % 4],
            "assigned_staff_id": (124 % 3) + 1,
            "taxi_included": True if 124 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_125(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #125 with realistic metadata."""
        day_offset = 125 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (125 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 125,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][125 % 4],
            "assigned_staff_id": (125 % 3) + 1,
            "taxi_included": True if 125 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_126(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #126 with realistic metadata."""
        day_offset = 126 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (126 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 126,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][126 % 4],
            "assigned_staff_id": (126 % 3) + 1,
            "taxi_included": True if 126 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_127(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #127 with realistic metadata."""
        day_offset = 127 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (127 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 127,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][127 % 4],
            "assigned_staff_id": (127 % 3) + 1,
            "taxi_included": True if 127 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_128(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #128 with realistic metadata."""
        day_offset = 128 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (128 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 128,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][128 % 4],
            "assigned_staff_id": (128 % 3) + 1,
            "taxi_included": True if 128 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_129(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #129 with realistic metadata."""
        day_offset = 129 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (129 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 129,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][129 % 4],
            "assigned_staff_id": (129 % 3) + 1,
            "taxi_included": True if 129 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_130(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #130 with realistic metadata."""
        day_offset = 130 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (130 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 130,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][130 % 4],
            "assigned_staff_id": (130 % 3) + 1,
            "taxi_included": True if 130 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_131(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #131 with realistic metadata."""
        day_offset = 131 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (131 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 131,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][131 % 4],
            "assigned_staff_id": (131 % 3) + 1,
            "taxi_included": True if 131 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_132(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #132 with realistic metadata."""
        day_offset = 132 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (132 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 132,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][132 % 4],
            "assigned_staff_id": (132 % 3) + 1,
            "taxi_included": True if 132 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_133(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #133 with realistic metadata."""
        day_offset = 133 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (133 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 133,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][133 % 4],
            "assigned_staff_id": (133 % 3) + 1,
            "taxi_included": True if 133 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_134(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #134 with realistic metadata."""
        day_offset = 134 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (134 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 134,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][134 % 4],
            "assigned_staff_id": (134 % 3) + 1,
            "taxi_included": True if 134 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_135(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #135 with realistic metadata."""
        day_offset = 135 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (135 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 135,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][135 % 4],
            "assigned_staff_id": (135 % 3) + 1,
            "taxi_included": True if 135 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_136(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #136 with realistic metadata."""
        day_offset = 136 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (136 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 136,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][136 % 4],
            "assigned_staff_id": (136 % 3) + 1,
            "taxi_included": True if 136 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_137(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #137 with realistic metadata."""
        day_offset = 137 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (137 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 137,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][137 % 4],
            "assigned_staff_id": (137 % 3) + 1,
            "taxi_included": True if 137 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_138(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #138 with realistic metadata."""
        day_offset = 138 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (138 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 138,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][138 % 4],
            "assigned_staff_id": (138 % 3) + 1,
            "taxi_included": True if 138 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_139(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #139 with realistic metadata."""
        day_offset = 139 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (139 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 139,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][139 % 4],
            "assigned_staff_id": (139 % 3) + 1,
            "taxi_included": True if 139 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_140(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #140 with realistic metadata."""
        day_offset = 140 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (140 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 140,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][140 % 4],
            "assigned_staff_id": (140 % 3) + 1,
            "taxi_included": True if 140 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_141(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #141 with realistic metadata."""
        day_offset = 141 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (141 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 141,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][141 % 4],
            "assigned_staff_id": (141 % 3) + 1,
            "taxi_included": True if 141 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_142(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #142 with realistic metadata."""
        day_offset = 142 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (142 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 142,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][142 % 4],
            "assigned_staff_id": (142 % 3) + 1,
            "taxi_included": True if 142 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_143(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #143 with realistic metadata."""
        day_offset = 143 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (143 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 143,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][143 % 4],
            "assigned_staff_id": (143 % 3) + 1,
            "taxi_included": True if 143 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_144(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #144 with realistic metadata."""
        day_offset = 144 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (144 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 144,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][144 % 4],
            "assigned_staff_id": (144 % 3) + 1,
            "taxi_included": True if 144 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_145(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #145 with realistic metadata."""
        day_offset = 145 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (145 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 145,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][145 % 4],
            "assigned_staff_id": (145 % 3) + 1,
            "taxi_included": True if 145 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_146(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #146 with realistic metadata."""
        day_offset = 146 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (146 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 146,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][146 % 4],
            "assigned_staff_id": (146 % 3) + 1,
            "taxi_included": True if 146 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_147(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #147 with realistic metadata."""
        day_offset = 147 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (147 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 147,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][147 % 4],
            "assigned_staff_id": (147 % 3) + 1,
            "taxi_included": True if 147 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_148(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #148 with realistic metadata."""
        day_offset = 148 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (148 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 148,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][148 % 4],
            "assigned_staff_id": (148 % 3) + 1,
            "taxi_included": True if 148 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_149(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #149 with realistic metadata."""
        day_offset = 149 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (149 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 149,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][149 % 4],
            "assigned_staff_id": (149 % 3) + 1,
            "taxi_included": True if 149 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_150(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #150 with realistic metadata."""
        day_offset = 150 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (150 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 150,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][150 % 4],
            "assigned_staff_id": (150 % 3) + 1,
            "taxi_included": True if 150 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_151(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #151 with realistic metadata."""
        day_offset = 151 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (151 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 151,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][151 % 4],
            "assigned_staff_id": (151 % 3) + 1,
            "taxi_included": True if 151 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_152(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #152 with realistic metadata."""
        day_offset = 152 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (152 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 152,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][152 % 4],
            "assigned_staff_id": (152 % 3) + 1,
            "taxi_included": True if 152 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_153(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #153 with realistic metadata."""
        day_offset = 153 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (153 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 153,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][153 % 4],
            "assigned_staff_id": (153 % 3) + 1,
            "taxi_included": True if 153 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_154(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #154 with realistic metadata."""
        day_offset = 154 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (154 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 154,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][154 % 4],
            "assigned_staff_id": (154 % 3) + 1,
            "taxi_included": True if 154 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_155(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #155 with realistic metadata."""
        day_offset = 155 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (155 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 155,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][155 % 4],
            "assigned_staff_id": (155 % 3) + 1,
            "taxi_included": True if 155 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_156(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #156 with realistic metadata."""
        day_offset = 156 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (156 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 156,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][156 % 4],
            "assigned_staff_id": (156 % 3) + 1,
            "taxi_included": True if 156 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_157(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #157 with realistic metadata."""
        day_offset = 157 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (157 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 157,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][157 % 4],
            "assigned_staff_id": (157 % 3) + 1,
            "taxi_included": True if 157 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_158(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #158 with realistic metadata."""
        day_offset = 158 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (158 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 158,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][158 % 4],
            "assigned_staff_id": (158 % 3) + 1,
            "taxi_included": True if 158 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_159(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #159 with realistic metadata."""
        day_offset = 159 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (159 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 159,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][159 % 4],
            "assigned_staff_id": (159 % 3) + 1,
            "taxi_included": True if 159 % 3 == 0 else False
        }

    @classmethod
    def generate_appointment_matrix_case_160(cls) -> Dict[str, Any]:
        """Synthetic appointment lifecycle scenario #160 with realistic metadata."""
        day_offset = 160 % 180
        target_date = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
        hour = 9 + (160 % 9)
        time_slot = f"{hour:02d}:00"
        return {
            "simulation_id": 160,
            "scheduled_date": target_date,
            "time_slot": time_slot,
            "service_category": ["อาบน้ำแมว", "สปาแมว", "ตัดแต่งขน", "ตัดเล็บ"][160 % 4],
            "assigned_staff_id": (160 % 3) + 1,
            "taxi_included": True if 160 % 3 == 0 else False
        }


def main():
    print("Feline Data Faker Engine Ready")
    sample = FelineDataFaker.generate_cat_profile(1, 42)
    print("Sample Generated Record:", sample["name"], "-", sample["breed"])


if __name__ == "__main__":
    main()
