import pandas as pd
import numpy as np
import os
import random
import mysql.connector
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pandas.conftest import ignore_doctest_warning

# -------------------
# CONFIG
# -------------------
load_dotenv()

def connect():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def insert_dataframe(df, table):
    cols = ", ".join(df.columns)
    placeholders = ", ".join(["%s"] * len(df.columns))
    sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"

    cursor.executemany(sql, df.values.tolist())
    conn.commit()

def generate_price(row):
    if row["product_type"] == "handgun":
        return np.random.uniform(400, 900)
    elif row["product_type"] == "rifle":
        return np.random.uniform(600, 1500)
    elif row["product_type"] == "ammo":
        return np.random.uniform(15, 60)
    else:
        return np.random.uniform(20, 200)

def get_order_attributes(prod_type):
    if prod_type in ["handgun", "rifle"]:
        return "pending_ffl", True
    return "completed", False

def get_caliber(prod_type):
    if prod_type == "handgun":
        return np.random.choice(["9mm", ".45 ACP", ".22", "10mm"])
    elif prod_type == "rifle":
        return np.random.choice(["5.56 NATO", "7.62x39", "12 Gauge", ".22"])
    elif prod_type == "ammo":
        return np.random.choice(["9mm", ".45 ACP", "5.56 NATO", "12 Gauge", ".22", "10mm", "7.62x39"])
    return None

def get_funnel_probabilities(prod_type, user_state):
    # Base probabilities
    if prod_type == "handgun":
        view_prob = 0.7
        add_prob = 0.35
        purchase_prob = 0.25
    elif prod_type == "rifle":
        view_prob = 0.65
        add_prob = 0.3
        purchase_prob = 0.22
    elif prod_type == "ammo":
        view_prob = 0.8
        add_prob = 0.5
        purchase_prob = 0.45
    else:  # accessory
        view_prob = 0.85
        add_prob = 0.55
        purchase_prob = 0.5

    # Regulatory friction
    if user_state in restricted_states:
        purchase_prob *= 0.7
        add_prob *= 0.85  # slight hesitation earlier in funnel

    return view_prob, add_prob, purchase_prob

def get_purchase_probability(prod_type, user_state):
    if prod_type in ["handgun", "rifle"]:
        prob = 0.3
    elif prod_type == "ammo":
        prob = 0.5
    else:
        prob = 0.65

    if user_state in restricted_states:
        prob *= 0.75

    return prob

def truncate_tables():
    # Truncate the tables prior to inserting
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    tables = ["orders", "events", "sessions", "experiment_assignments", "products", "users"]

    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table}")

    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

np.random.seed(42)

NUM_USERS = 10000
NUM_PRODUCTS = 50

# -------------------
# GENERATE DATA
# -------------------

users = pd.DataFrame({
    "user_id": range(1, NUM_USERS + 1),
    "signup_date": pd.to_datetime("2025-01-01") + pd.to_timedelta(np.random.randint(0, 90, NUM_USERS), unit='D'),
    "state": np.random.choice(
    ["CA", "TX", "FL", "AZ", "NV", "WA", "OR", "CO", "UT", "ID", "TN", "KY"], NUM_USERS,
       p=[0.16, 0.15, 0.12, 0.10, 0.08, 0.05, 0.07, 0.07, 0.08, 0.07, 0.03, 0.02]),
    "device_type": np.random.choice(["mobile", "desktop"], NUM_USERS, p=[0.7, 0.3]),
    "acquisition_channel": np.random.choice(["paid_search", "organic", "email", "social"], NUM_USERS)
})

products = pd.DataFrame({
    "product_id": range(1, NUM_PRODUCTS + 1),
    "product_type": np.random.choice(["handgun", "rifle", "accessory", "ammo"], NUM_PRODUCTS, p=[0.2, 0.15, 0.45, 0.2])
})

# Conditional caliber
products["caliber"] = products["product_type"].apply(get_caliber)
products["manufacturer"] = np.random.choice(["Glock", "Smith & Wesson", "Sig Sauer", "Ruger", "Springfield"], NUM_PRODUCTS)
products["requires_ffl"] = products["product_type"].isin(["handgun", "rifle"])
products["price"] = products.apply(generate_price, axis=1)
products["cost"] = products["price"] * np.random.uniform(0.5, 0.8, NUM_PRODUCTS)
products = products.replace({np.nan: None})

# print(products.to_string())

experiment = pd.DataFrame({
    "user_id": users["user_id"],
    "experiment_name": "compliance_ui_test",
    "variant": np.random.choice(["control", "treatment"], NUM_USERS),
    "assignment_date": pd.to_datetime("2025-02-01")
})

sessions = []
session_id = 1

for user in users["user_id"]:
    for _ in range(np.random.randint(1, 5)):
        start = datetime(2025, 2, 1) + timedelta(days=np.random.randint(0, 30))
        sessions.append([
            session_id,
            user,
            start,
            start + timedelta(minutes=np.random.randint(1, 30)),
            random.choice(["paid_search", "organic", "email", "social"]),
            random.choice(["mobile", "desktop"])
        ])
        session_id += 1

sessions = pd.DataFrame(sessions, columns=[
    "session_id", "user_id", "session_start", "session_end",
    "traffic_source", "device_type"
])

events = []
orders = []
event_id = 1
order_id = 1

restricted_states = ["CA", "WA", "NY"]
product_type_lookup = dict(zip(products.product_id, products.product_type))
price_lookup = dict(zip(products.product_id, products.price))

for session in sessions.itertuples(index=False, name="Session"):
    product = np.random.choice(products["product_id"])
    product_type = product_type_lookup[product]
    state = users.loc[users.user_id == session.user_id, "state"].values[0]

    view_probability, add_probability, purchase_probability = get_funnel_probabilities(product_type, state)

    viewed = np.random.rand() < view_probability
    added = viewed and np.random.rand() < add_probability

    ffl_submitted = False
    if added and product_type in ["handgun", "rifle"]:
        ffl_submitted = np.random.rand() < 0.85  # some drop-off here
        purchased = added and ffl_submitted and (np.random.rand() < purchase_probability)
    else:
        purchased = added and (np.random.rand() < purchase_probability)

    if viewed:
        events.append([event_id, session.session_id, session.user_id, "view_product", product, session.session_start])
        event_id += 1

    if added:
        events.append([event_id, session.session_id, session.user_id, "add_to_cart", product, session.session_start])
        event_id += 1

    if ffl_submitted:
        events.append([event_id, session.session_id, session.user_id, "ffl_submitted", product, session.session_start])
        event_id += 1

    if purchased:
        price = price_lookup[product]
        # Determine order attributes
        order_status, shipped_to_ffl = get_order_attributes(product_type)
        events.append([event_id, session.session_id, session.user_id, "purchase", product, session.session_start])
        orders.append([order_id, session.user_id, session.session_id, session.session_start, order_status, shipped_to_ffl, price])
        event_id += 1
        order_id += 1

events = pd.DataFrame(events, columns=[
    "event_id", "session_id", "user_id", "event_type", "product_id", "event_timestamp"
])

orders = pd.DataFrame(orders, columns=[
    "order_id", "user_id", "session_id", "order_timestamp", "order_status", "shipped_to_ffl", "revenue"
])

# -------------------
# LOAD INTO MYSQL
# -------------------

conn = connect()
cursor = conn.cursor()

# Truncate tables prior to data insertion
truncate_tables()

# Insert order matters (FK constraints)
insert_dataframe(users, "users")
insert_dataframe(products, "products")
insert_dataframe(experiment, "experiment_assignments")
insert_dataframe(sessions, "sessions")
insert_dataframe(events, "events")
insert_dataframe(orders, "orders")

cursor.close()
conn.close()

print("✅ Data successfully loaded into MySQL!")