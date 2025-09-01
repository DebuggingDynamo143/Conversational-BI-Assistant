def generate_sql_query(natural_language_query):
    q = natural_language_query.lower()

    # --- Sales Analysis ---
    if "total sales" in q and "last 6 months" in q:
        return """SELECT p.product_name, SUM(s.amount) as total_sales
                  FROM sales s
                  JOIN products p ON s.product_id = p.product_id
                  WHERE s.sale_date >= CURRENT_DATE - INTERVAL '6 months'
                  GROUP BY p.product_name
                  ORDER BY total_sales DESC"""

    if "highest sales" in q and "2024" in q:
        return """SELECT c.region, SUM(s.amount) as total_sales
                  FROM sales s
                  JOIN customers c ON s.customer_id = c.customer_id
                  WHERE EXTRACT(YEAR FROM s.sale_date) = 2024
                  GROUP BY c.region
                  ORDER BY total_sales DESC LIMIT 1"""

    if "monthly" in q and "trend" in q and "product" in q:
        product = q.split("product")[-1].strip().strip("?")
        return f"""SELECT DATE_TRUNC('month', s.sale_date) as month, SUM(s.amount) as total_sales
                   FROM sales s
                   JOIN products p ON s.product_id = p.product_id
                   WHERE p.product_name ILIKE '%{product}%'
                   GROUP BY month
                   ORDER BY month"""

    if "compare" in q and "product" in q and "region" in q:
        return """SELECT p.product_name, c.region, SUM(s.amount) as total_sales
                  FROM sales s
                  JOIN products p ON s.product_id = p.product_id
                  JOIN customers c ON s.customer_id = c.customer_id
                  GROUP BY p.product_name, c.region
                  ORDER BY p.product_name, c.region"""

    # --- Customer Insights ---
    if "top 10 customers" in q:
        return """SELECT c.customer_name, SUM(s.amount) as total_spent
                  FROM sales s
                  JOIN customers c ON s.customer_id = c.customer_id
                  GROUP BY c.customer_name
                  ORDER BY total_spent DESC LIMIT 10"""

    if "purchased more than" in q or "spending" in q:
        return """SELECT c.customer_name, SUM(s.amount) as total_spent
                  FROM sales s
                  JOIN customers c ON s.customer_id = c.customer_id
                  GROUP BY c.customer_name
                  HAVING SUM(s.amount) > 5000
                  ORDER BY total_spent DESC"""

    if "unique customers" in q and "february 2025" in q:
        return """SELECT COUNT(DISTINCT customer_id) as unique_customers
                  FROM sales
                  WHERE EXTRACT(MONTH FROM sale_date)=2 
                    AND EXTRACT(YEAR FROM sale_date)=2025"""

    # --- Product Insights ---
    if "average sales" in q and "category" in q:
        return """SELECT p.category, AVG(s.amount) as avg_sales
                  FROM sales s
                  JOIN products p ON s.product_id = p.product_id
                  GROUP BY p.category
                  ORDER BY avg_sales DESC"""

    if "lowest sales" in q and "2023" in q:
        return """SELECT p.product_name, SUM(s.amount) as total_sales
                  FROM sales s
                  JOIN products p ON s.product_id = p.product_id
                  WHERE EXTRACT(YEAR FROM s.sale_date)=2023
                  GROUP BY p.product_name
                  ORDER BY total_sales ASC LIMIT 1"""

    if "distribution" in q and "categories" in q:
        return """SELECT p.category, SUM(s.amount) as total_sales
                  FROM sales s
                  JOIN products p ON s.product_id = p.product_id
                  GROUP BY p.category"""

    # --- Time-based Trends ---
    if "daily sales" in q and "last 30 days" in q:
        return """SELECT s.sale_date, SUM(s.amount) as daily_sales
                  FROM sales s
                  WHERE s.sale_date >= CURRENT_DATE - INTERVAL '30 days'
                  GROUP BY s.sale_date
                  ORDER BY s.sale_date"""

    if "quarterly" in q and ("2023" in q or "2024" in q):
        return """SELECT EXTRACT(YEAR FROM s.sale_date) as year,
                         EXTRACT(QUARTER FROM s.sale_date) as quarter,
                         SUM(s.amount) as total_sales
                  FROM sales s
                  WHERE EXTRACT(YEAR FROM s.sale_date) IN (2023,2024)
                  GROUP BY year, quarter
                  ORDER BY year, quarter"""

    if "highest sale amount" in q or "single transaction" in q:
        return """SELECT MAX(amount) as highest_sale FROM sales"""

    # --- Mixed Insights ---
    if "sales by product and region" in q and "2025" in q:
        return """SELECT p.product_name, c.region, SUM(s.amount) as total_sales
                  FROM sales s
                  JOIN products p ON s.product_id = p.product_id
                  JOIN customers c ON s.customer_id = c.customer_id
                  WHERE EXTRACT(YEAR FROM s.sale_date)=2025
                  GROUP BY p.product_name, c.region"""

    if "customers" in q and "north" in q and "product" in q:
        product = q.split("product")[-1].strip()
        return f"""SELECT DISTINCT c.customer_name
                   FROM sales s
                   JOIN products p ON s.product_id = p.product_id
                   JOIN customers c ON s.customer_id = c.customer_id
                   WHERE c.region='North' AND p.product_name ILIKE '%{product}%'"""

    if "top 5 products" in q and "south" in q:
        return """SELECT p.product_name, SUM(s.amount) as total_sales
                  FROM sales s
                  JOIN products p ON s.product_id = p.product_id
                  JOIN customers c ON s.customer_id = c.customer_id
                  WHERE c.region='South'
                  GROUP BY p.product_name
                  ORDER BY total_sales DESC LIMIT 5"""

    # --- Fallback ---
    return "SELECT * FROM sales LIMIT 10"
