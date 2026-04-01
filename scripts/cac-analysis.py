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

# Simulated marketing spend
spend = pd.DataFrame({
    "channel": ["paid_search", "organic", "email", "social"],
    "cost": [2000, 500, 300, 800]
})

query = """
SELECT
    acquisition_channel,
    COUNT(DISTINCT user_id) AS users
FROM users
GROUP BY acquisition_channel;
"""

users = pd.read_sql(query, conn)

df = users.merge(spend, left_on="acquisition_channel", right_on="channel")

# CAC calculation
df["cac"] = df["cost"] / df["users"]

# Rank channels (lower CAC = better)
df["cac_rank"] = df["cac"].rank(method="dense", ascending=True)

# Sort for readability
df = df.sort_values("cac_rank")

print("\n=== CAC ANALYSIS (RANKED) ===")
print(df[["acquisition_channel", "cost", "users", "cac", "cac_rank"]])

# Optional: highlight best/worst
best_channel = df.iloc[0]
worst_channel = df.iloc[-1]

print(f"\n🏆 Best Channel (Lowest CAC): {best_channel.acquisition_channel} (${best_channel.cac:.2f})")
print(f"⚠️ Worst Channel (Highest CAC): {worst_channel.acquisition_channel} (${worst_channel.cac:.2f})")

# Estimate revenue (simple version)
revenue_query = """
SELECT
    u.acquisition_channel,
    SUM(o.revenue) AS total_revenue
FROM users u
JOIN orders o ON u.user_id = o.user_id
GROUP BY u.acquisition_channel;
"""

revenue = pd.read_sql(revenue_query, conn)

df = df.merge(revenue, on="acquisition_channel", how="left")

df["profit"] = df["total_revenue"] - df["cost"]

print('\nOverall Channel Profitability:\n', df.to_string())

conn.close()