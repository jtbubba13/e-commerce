import pandas as pd
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

query = """
SELECT
    -- u.state,
    -- p.product_type,
    COUNT(DISTINCT CASE WHEN event_type = 'view_product' THEN session_id END) AS views,
    COUNT(DISTINCT CASE WHEN event_type = 'add_to_cart' THEN session_id END) AS adds,
    COUNT(DISTINCT CASE WHEN event_type = 'add_to_cart' and p.requires_ffl = true THEN session_id END) AS firearm_adds,
    COUNT(DISTINCT CASE WHEN event_type = 'ffl_submitted' THEN session_id END) AS ffl,
    COUNT(DISTINCT CASE WHEN event_type = 'purchase' and p.requires_ffl = true THEN session_id END) AS firearm_purchases,
    COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN session_id END) AS purchases
FROM events e
JOIN users u ON e.user_id = u.user_id
JOIN products p ON e.product_id = p.product_id
-- GROUP BY u.state, p.product_type
;
"""

df = pd.read_sql(query, conn)

views = df.views[0]
adds = df.adds[0]
fa_adds = df.firearm_adds[0]
ffl = df.ffl[0]
fa_purchases = df.firearm_purchases[0]
purchases = df.purchases[0]

print("\n=== FUNNEL ANALYSIS ===")
print(f"Views: {views}")
print(f"Add to Cart: {adds} ({adds/views:.2%})")
print(f"Firearm Add to Cart: {fa_adds} ({fa_adds/views:.2%})")
print(f"FFL Submitted: {ffl} ({ffl/fa_adds:.2%})")
print(f"Firearm Purchased: {fa_purchases} ({fa_purchases/ffl:.2%})")
print(f"Purchases: {purchases} ({purchases/adds:.2%})")

conn.close()