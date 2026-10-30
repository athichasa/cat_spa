import urllib.request
import re
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("=== STARTING TESTS FOR 3 ISSUES ===")

# 1. Landing Page Review Stars Check
req_home = urllib.request.Request("http://127.0.0.1:5000/", headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req_home) as resp:
    html = resp.read().decode('utf-8')
    assert resp.status == 200

    # Find review-stars-pill instances
    pills = re.findall(r'<div class="review-stars-pill"[^>]*>(.*?)</div>', html, re.DOTALL)
    print(f"[TEST 1] Found {len(pills)} review rating pills on landing page")
    assert len(pills) > 0, "No review pills found!"
    for p in pills:
        assert "★" not in p, f"Found star character in pill: {p}"
        assert "5.0" in p, f"Expected 5.0 in pill, got: {p}"
    print("  -> TEST 1 PASSED: Only '5.0' is shown, no star icons in cards!")

# 2. Check Cat Illustrations for Calendar
assets = ['cal_peeking_cat.png', 'cal_sleeping_cat.png', 'cal_yarn_ball.png', 'cal_corner_cat.png']
for a in assets:
    p = os.path.join('static', 'images', a)
    assert os.path.exists(p), f"Asset {p} does not exist!"
    print(f"[TEST 2] Verified asset exists: {p} ({os.path.getsize(p)} bytes)")
print("  -> TEST 2 PASSED: All 4 cute cat assets exist!")

# 3. Check Dashboard Calendar HTML & CSS
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash_html = f.read()

assert 'cal_peeking_cat.png' in dash_html, "Peeking cat not in dashboard.html"
assert 'cal_yarn_ball.png' in dash_html, "Yarn ball not in dashboard.html"
assert 'cal_sleeping_cat.png' in dash_html, "Sleeping cat not in dashboard.html"
assert 'cal_corner_cat.png' in dash_html, "Corner cat not in dashboard.html"
assert 'รอคอนเฟิร์ม' in dash_html, "รอคอนเฟิร์ม not in legend"
print("[TEST 3] Dashboard HTML cute cat elements verified!")

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

assert '.cal-day-cell::before' in css, "Cat ears ::before missing in CSS"
assert '.cal-day-cell::after' in css, "Cat ears ::after missing in CSS"
assert '.cal-peeking-cat' in css, ".cal-peeking-cat missing in CSS"
assert '.cal-sleeping-cat' in css, ".cal-sleeping-cat missing in CSS"
assert '.cal-yarn-ball' in css, ".cal-yarn-ball missing in CSS"
assert '.cal-corner-cat' in css, ".cal-corner-cat missing in CSS"
print("[TEST 4] CSS cat ears and illustrations styling verified!")

# 4. Check Notification Logic
with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

assert 'urgent_notifications' in app_code, "urgent_notifications missing in app.py"
assert 'review_notifications' in app_code, "review_notifications missing in app.py"

with open('templates/bookings.html', 'r', encoding='utf-8') as f:
    bk_html = f.read()

assert '{% if urgent_notifications and urgent_notifications_count > 0 %}' in bk_html, "urgent_notifications condition missing in bookings.html"
assert '!notifBellBtn.contains(e.target)' in bk_html, "notifBellBtn contains check missing in bookings.html"
assert 'item-completed' in bk_html, "item-completed missing in bookings.html dropdown"
print("[TEST 5] Notification logic and dropdown click handler verified!")

print("=== ALL TESTS PASSED WITH 100% SUCCESS ===")
