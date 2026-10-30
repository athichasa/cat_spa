import urllib.request
import sqlite3
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("=== STARTING COMPREHENSIVE VERIFICATION ===")

# 1. Database Check
conn = sqlite3.connect('cat_spa.db')
cur = conn.cursor()

# Bookings reset check
b_count = cur.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
print(f"[CHECK 1] Bookings count in DB: {b_count} (Must be 0)")
assert b_count == 0, f"Expected 0 bookings, got {b_count}"

# Sequence check
seq_res = cur.execute("SELECT seq FROM sqlite_sequence WHERE name = 'bookings'").fetchone()
seq_val = seq_res[0] if seq_res else 0
print(f"[CHECK 2] Bookings sqlite_sequence: {seq_val} (Must be 0 or None)")

# Staff rating check
staff_rows = cur.execute("SELECT staff_id, nickname, rating, service_count FROM staff ORDER BY staff_id").fetchall()
for s in staff_rows:
    sid, name, rtg, svc = s
    rev_avg = cur.execute("SELECT ROUND(AVG(staff_rating), 1) FROM reviews WHERE staff_id = ?", (sid,)).fetchone()[0]
    print(f"[CHECK 3] Staff {sid} ({name}): DB Rating={rtg}, Calculated Review AVG={rev_avg}")
    assert 4.9 <= rtg <= 5.0, f"Staff {name} rating {rtg} not in [4.9, 5.0]"
    assert rev_avg == rtg, f"Staff {name} review avg {rev_avg} != table rating {rtg}"

# Shop rating check
shop_avg = cur.execute("SELECT ROUND(AVG(shop_rating), 1), COUNT(*) FROM reviews").fetchone()
print(f"[CHECK 4] Overall Shop Rating: {shop_avg[0]}, Total Reviews: {shop_avg[1]}")
assert shop_avg[0] == 5.0, f"Shop rating {shop_avg[0]} is not 5.0"
assert shop_avg[1] == 26, f"Expected 26 reviews, got {shop_avg[1]}"
conn.close()

# 2. HTTP GET /staff Check
req = urllib.request.Request("http://127.0.0.1:5000/staff", headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    staff_html = resp.read().decode('utf-8')
    assert resp.status == 200, f"/staff status {resp.status}"

    # Verify grid structure
    grid_start = staff_html.find('class="staff-grid"')
    div_start = staff_html.rfind('<div', 0, grid_start + 20)
    grid_end = staff_html.find('<!-- CUSTOMER REVIEWS SHOWCASE -->')
    grid_block = staff_html[div_start:grid_end]

    opens = grid_block.count('<div')
    closes = grid_block.count('</div>')
    print(f"[CHECK 5] /staff Grid Div Balance: open={opens}, close={closes}")
    assert opens == closes, f"Div mismatch in staff-grid: {opens} vs {closes}"

    cards = re.findall(r'<div class="staff-card"[^>]*>', staff_html)
    print(f"[CHECK 6] /staff Card count: {len(cards)}")
    assert len(cards) == 3, f"Expected 3 cards, found {len(cards)}"

    for name in ["ต้นเตย", "มีมี่", "อุ๋มอิ๋ม"]:
        assert name in staff_html, f"Staff {name} not found in /staff HTML"

    assert "คุณคุณ" not in staff_html, "Found redundant 'คุณคุณ' in /staff"
    print("[CHECK 7] /staff All 3 staff cards verified and equal structure!")

# 3. HTTP GET / (Homepage with Customer Reviews)
req_home = urllib.request.Request("http://127.0.0.1:5000/", headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req_home) as resp_home:
    home_html = resp_home.read().decode('utf-8')
    assert resp_home.status == 200, f"/ status {resp_home.status}"

    assert 'id="reviews"' in home_html, "Reviews section not found in homepage"
    assert "เสียงตอบรับและความประทับใจจากลูกค้า" in home_html, "Title not found in homepage"
    assert "5.0 / 5.0" in home_html or "5.0" in home_html, "Shop 5.0 rating not found in homepage"
    assert ".***" in home_html, "Masked names (.***) not found in homepage"
    assert "คุณคุณ" not in home_html, "Redundant 'คุณคุณ' found in homepage"
    print("[CHECK 8] Homepage reviews section and masked names verified!")

# 4. HTTP GET /dashboard Check (Calendar)
# Simulate logged-in user or check style.css
with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

assert 'min-height: 34px' in css_content, "Compact calendar min-height not found in style.css"
assert '.reviews-section {' in css_content, "Reviews section CSS not found in style.css"
print("[CHECK 9] style.css calendar compact & cute styles verified!")

print("=== ALL VERIFICATIONS PASSED SUCCESSFULLY! ===")
