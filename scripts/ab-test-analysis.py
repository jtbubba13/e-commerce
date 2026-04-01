import pandas as pd
import mysql.connector
import os
from dotenv import load_dotenv
from statsmodels.stats.proportion import proportions_ztest

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

query = """
SELECT
    ea.variant,
    COUNT(DISTINCT s.session_id) AS sessions,
    COUNT(DISTINCT o.order_id) AS orders
FROM sessions s
JOIN experiment_assignments ea ON s.user_id = ea.user_id
LEFT JOIN orders o ON s.session_id = o.session_id
GROUP BY ea.variant;
"""

df = pd.read_sql(query, conn)

df["conversion_rate"] = df["orders"] / df["sessions"]

# Extract values
control = df[df.variant == "control"]
treatment = df[df.variant == "treatment"]

count = [treatment.orders.values[0], control.orders.values[0]]
nobs = [treatment.sessions.values[0], control.sessions.values[0]]

stat, pval = proportions_ztest(count, nobs)

lift = (treatment.conversion_rate.values[0] - control.conversion_rate.values[0]) / control.conversion_rate.values[0]

print("\n=== A/B TEST RESULTS ===")
print(df.to_string())
print(f"\nLift: {lift:.2%}")
print(f"P-value: {pval:.4f}")

if pval < 0.05:
    print("✅ Statistically significant result")
else:
    print("❌ Not statistically significant")

conn.close()