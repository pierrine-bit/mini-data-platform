-- 1. Total Sales
SELECT 
    SUM(amount) AS total_sales
FROM sales;

-- 2. Sales by Product
SELECT 
    product,
    SUM(amount) AS total_sales
FROM sales
GROUP BY product
ORDER BY total_sales DESC;

-- 3. Sales by Region
SELECT 
    region,
    SUM(amount) AS total_sales
FROM sales
GROUP BY region
ORDER BY total_sales DESC;

-- 4. Daily Sales Trend
SELECT 
    DATE(order_date) AS order_day,
    SUM(amount) AS total_sales
FROM sales
GROUP BY order_day
ORDER BY order_day;

-- 5. Monthly Sales Trend
SELECT 
    DATE_TRUNC('month', order_date) AS month,
    SUM(amount) AS total_sales
FROM sales
GROUP BY month
ORDER BY month;

-- 6. Top 10 Customers by Sales
SELECT 
    customer_id,
    SUM(amount) AS total_spent
FROM sales
GROUP BY customer_id
ORDER BY total_spent DESC
LIMIT 10;

-- 7. Average Order Value
SELECT 
    AVG(amount) AS average_order_value
FROM sales;

-- 8. Total Orders by Product
SELECT 
    product,
    COUNT(*) AS total_orders
FROM sales
GROUP BY product
ORDER BY total_orders DESC;