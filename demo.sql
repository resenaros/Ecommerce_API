-- 1. Create the database
CREATE DATABASE IF NOT EXISTS ecommerce_api;

-- 2. Use the new database
USE ecommerce_api;

-- 3. Show all tables
SHOW TABLES;

-- 4. Select all records from the customer table
SELECT * FROM customer;

-- 5. Select all records from the products table
SELECT * FROM products;

-- 6. Select all orders and see the order_date column
SELECT * FROM orders;

-- 7. Select all records from the order_products association table
SELECT * FROM order_products;

-- 8. Alter the order_date column in orders to ensure it's DATETIME and NOT NULL
ALTER TABLE orders MODIFY order_date DATETIME NOT NULL;

-- 9. Check the structure of the orders table after alteration
DESCRIBE orders;