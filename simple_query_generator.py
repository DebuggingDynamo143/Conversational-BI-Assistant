def generate_sql_query(natural_language_query):
    """
    Simple rule-based SQL query generator with Oracle-compatible syntax
    """
    query = natural_language_query.lower()
    
    # Pattern matching for different types of queries
    if any(word in query for word in ["last 5", "recent", "show me", "display"]):
        return "SELECT * FROM (SELECT * FROM sales ORDER BY sale_date DESC) WHERE ROWNUM <= 5"
    
    elif "total sales" in query and "product" in query:
        return "SELECT product_name, SUM(amount) as total_sales FROM sales GROUP BY product_name ORDER BY total_sales DESC"
    
    elif "average" in query and "product" in query:
        return "SELECT product_name, AVG(amount) as average_sale FROM sales GROUP BY product_name ORDER BY average_sale DESC"
    
    elif "region" in query and ("compare" in query or "by region" in query):
        return "SELECT region, SUM(amount) as total_sales FROM sales GROUP BY region ORDER BY total_sales DESC"
    
    elif "february" in query or "2" in query or "second month" in query:
        return "SELECT product_name, SUM(amount) as total_sales FROM sales WHERE EXTRACT(MONTH FROM sale_date) = 2 AND EXTRACT(YEAR FROM sale_date) = 2023 GROUP BY product_name"
    
    elif "trend" in query or "over time" in query or "by date" in query:
        return "SELECT sale_date, SUM(amount) as daily_sales FROM sales GROUP BY sale_date ORDER BY sale_date"
    
    elif "product x" in query:
        return "SELECT * FROM sales WHERE product_name = 'Product X' ORDER BY sale_date"
    
    elif "product y" in query:
        return "SELECT * FROM sales WHERE product_name = 'Product Y' ORDER BY sale_date"
    
    elif "north" in query or "south" in query:
        if "north" in query and "south" in query:
            return "SELECT region, SUM(amount) as total_sales FROM sales WHERE region IN ('North', 'South') GROUP BY region ORDER BY total_sales DESC"
        elif "north" in query:
            return "SELECT * FROM sales WHERE region = 'North' ORDER BY sale_date"
        else:
            return "SELECT * FROM sales WHERE region = 'South' ORDER BY sale_date"
    
    elif "amount" in query and "average" in query:
        return "SELECT product_name, AVG(amount) as average_amount FROM sales GROUP BY product_name ORDER BY average_amount DESC"
    
    elif "amount" in query and "sum" in query:
        return "SELECT product_name, SUM(amount) as total_amount FROM sales GROUP BY product_name ORDER BY total_amount DESC"
    
    elif "product" in query and "region" in query:
        return "SELECT product_name, region, SUM(amount) as total_sales FROM sales GROUP BY product_name, region ORDER BY product_name, region"
    
    # Default fallback - try to be more specific
    return "SELECT * FROM (SELECT * FROM sales ORDER BY id DESC) WHERE ROWNUM <= 10"