import google.generativeai as genai
import os
from dotenv import load_dotenv
from postgresql_database import get_db_schema

load_dotenv()

def get_gemini_api_key():
    """Get Gemini API key from env or Streamlit secrets."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        try:
            import streamlit as st
            api_key = st.secrets.get("GEMINI_API_KEY")
        except:
            pass
    return api_key

def generate_sql_query(natural_language_query):
    api_key = get_gemini_api_key()
    if not api_key:
        return generate_fallback_query(natural_language_query)

    try:
        genai.configure(api_key=api_key)

        schema_text = get_db_schema()
        print("🔎 Injected DB Schema:")
        print(schema_text)

        prompt = f"""
        You are an expert SQL generator.
        Convert the following natural language request into a valid PostgreSQL SQL query.

        Database schema:
        {schema_text}

        Rules:
        - Use PostgreSQL syntax.
        - For limiting results, use: LIMIT N
        - Use EXTRACT(MONTH FROM sale_date) for month filters
        - Always JOIN products and customers when referencing product_name or customer_name.
        - Only return the SQL query (no explanation, no markdown).

        Natural language query: {natural_language_query}
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        print("🔎 Gemini Raw Response:")
        print(response.text)

        sql_query = response.text.strip()

        # Cleanup if wrapped in markdown fences
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]

        return sql_query.strip()
    except Exception as e:
        print(f"❌ Error with Gemini API: {e}")
        return generate_fallback_query(natural_language_query)

def generate_fallback_query(natural_language_query):
    query = natural_language_query.lower()

    if "last 5" in query:
        return """SELECT s.sale_id, p.product_name, c.customer_name, s.amount, s.sale_date
                  FROM sales s
                  JOIN products p ON s.product_id = p.product_id
                  JOIN customers c ON s.customer_id = c.customer_id
                  ORDER BY s.sale_date DESC LIMIT 5"""
    elif "total sales" in query and "product" in query:
        return """SELECT p.product_name, SUM(s.amount) AS total_sales
                  FROM sales s
                  JOIN products p ON s.product_id = p.product_id
                  GROUP BY p.product_name ORDER BY total_sales DESC"""
    elif "average" in query and "product" in query:
        return """SELECT p.product_name, AVG(s.amount) AS average_sale
                  FROM sales s
                  JOIN products p ON s.product_id = p.product_id
                  GROUP BY p.product_name ORDER BY average_sale DESC"""
    elif "north" in query or "south" in query:
        return """SELECT c.region, SUM(s.amount) AS total_sales
                  FROM sales s
                  JOIN customers c ON s.customer_id = c.customer_id
                  WHERE c.region IN ('North', 'South')
                  GROUP BY c.region"""
    elif "february" in query:
        return """SELECT p.product_name, SUM(s.amount) AS total_sales
                  FROM sales s
                  JOIN products p ON s.product_id = p.product_id
                  WHERE EXTRACT(MONTH FROM s.sale_date) = 2
                  GROUP BY p.product_name"""
    return "SELECT * FROM sales LIMIT 10"
