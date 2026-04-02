Create database ecommerce;

Use ecommerce;

-- USERS
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    signup_date DATE,
    state VARCHAR(10),
    device_type VARCHAR(20),
    acquisition_channel VARCHAR(50)
);

-- SESSIONS
CREATE TABLE sessions (
    session_id INT PRIMARY KEY,
    user_id INT,
    session_start DATETIME,
    session_end DATETIME,
    traffic_source VARCHAR(50),
    device_type VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- PRODUCTS
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_type VARCHAR(50),
    caliber VARCHAR(20),
    manufacturer VARCHAR(50),
    requires_ffl BOOLEAN,
    price DECIMAL(10,2),
    cost DECIMAL(10,2)
);

-- EVENTS
CREATE TABLE events (
    event_id INT PRIMARY KEY,
    session_id INT,
    user_id INT,
    event_type VARCHAR(50),
    product_id INT,
    event_timestamp DATETIME,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- ORDERS
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT,
    session_id INT,
    order_timestamp DATETIME,
    order_status VARCHAR(50),
    shipped_to_ffl BOOLEAN,
    revenue DECIMAL(10,2),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- EXPERIMENT ASSIGNMENTS
CREATE TABLE experiment_assignments (
    user_id INT,
    experiment_name VARCHAR(100),
    variant VARCHAR(20),
    assignment_date DATE,
    PRIMARY KEY (user_id, experiment_name),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
