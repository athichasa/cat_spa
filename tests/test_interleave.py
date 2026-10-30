import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

def mask_customer_name(name):
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

conn = sqlite3.connect('cat_spa.db')
conn.row_factory = sqlite3.Row

staff_list_active = conn.execute("SELECT staff_id, nickname FROM staff WHERE is_active = 1 ORDER BY staff_id ASC").fetchall()

shop_reviews = []
reviews_by_staff = {}
for st in staff_list_active:
    s_id = st["staff_id"]
    rows = conn.execute("""
        SELECT review_id, user_name, cat_name, staff_name, service_name,
               shop_rating, shop_comment, staff_rating, staff_comment, created_at
        FROM reviews
        WHERE staff_id = ? AND ((shop_comment IS NOT NULL AND shop_comment != '') OR (staff_comment IS NOT NULL AND staff_comment != ''))
        ORDER BY review_id DESC
        LIMIT 3
    """, (s_id,)).fetchall()
    reviews_by_staff[s_id] = [dict(r) for r in rows]

max_len = max((len(lst) for lst in reviews_by_staff.values()), default=0)
for i in range(max_len):
    for st in staff_list_active:
        lst = reviews_by_staff.get(st["staff_id"], [])
        if i < len(lst):
            rd = lst[i]
            rd["masked_user_name"] = mask_customer_name(rd.get("user_name", ""))
            shop_reviews.append(rd)

print(f"Total reviews selected: {len(shop_reviews)}")
for idx, r in enumerate(shop_reviews, 1):
    print(f"Card {idx}: {r['masked_user_name']} (น้อง{r['cat_name']}) - ดูแลโดย คุณ{r['staff_name']} [{r['service_name']}]")
    print(f"        Comment: \"{r['shop_comment'] or r['staff_comment']}\"")
conn.close()
