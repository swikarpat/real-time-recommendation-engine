-- Create the user_interactions table
CREATE TABLE user_interactions (
    user_id INT,
    product_id INT,
    event_type VARCHAR(255),
    timestamp TIMESTAMP,
    session_id VARCHAR(255),
    metadata JSON
);

-- Create the products table
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(255),
    price DECIMAL(10, 2),
    description TEXT,
    attributes JSON
);

-- Create the users table (if you are collecting user data)
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    user_name VARCHAR(255),
    email VARCHAR(255),
    demographics JSON
);