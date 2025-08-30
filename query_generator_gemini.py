import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def generate_sql_query(natural_language_query):
    # Check if API key is available
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return generate_fallback_query(natural_language_query)
    
    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        prompt = f"""
        You are an expert data analyst. Convert the following natural language query into Oracle SQL.
        The database has a table named 'sales' with columns: id, product_name, sale_date, amount, region.
        
        Important: 
        - Use Oracle SQL syntax compatible with older versions (avoid FETCH FIRST, use ROWNUM instead)
        - Return only the SQL query without any explanation
        - Do not include markdown formatting or backticks
        - Make sure the query is specific to the question asked
        - For limiting results, use: SELECT * FROM (SELECT ... ORDER BY ...) WHERE ROWNUM <= N
        - Use SUM() instead of SDN() for summation
        
        Natural language query: {natural_language_query}
        """
        
        # Try different model names
        model_names = ['gemini-pro', 'models/gemini-pro']
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                
                sql_query = response.text.strip()
                
                # Clean up the response
                if sql_query.startswith("```sql"):
                    sql_query = sql_query[6:]
                if sql_query.startswith("```"):
                    sql_query = sql_query[3:]
                if sql_query.endswith("```"):
                    sql_query = sql_query[:-3]
                
                # Fix common SQL errors
                sql_query = sql_query.replace("SDN(", "SUM(")
                
                # Validate that it looks like a SQL query
                if "select" in sql_query.lower() and "from" in sql_query.lower():
                    return sql_query.strip()
                
            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                continue
        
        # If all models fail, use fallback
        return generate_fallback_query(natural_language_query)
    
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        return generate_fallback_query(natural_language_query)

def generate_fallback_query(natural_language_query):
    """
    Improved fallback query generator with Oracle-compatible syntax
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
    
    elif "product" in query and "region" in query:
        return "SELECT product_name, region, SUM(amount) as total_sales FROM sales GROUP BY product_name, region ORDER BY product_name, region"
    
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
    
    # Default fallback - try to be more specific
    return "SELECT * FROM (SELECT * FROM sales ORDER BY id DESC) WHERE ROWNUM <= 10"