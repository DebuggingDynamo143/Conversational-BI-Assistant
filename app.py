import streamlit as st
import pandas as pd
import plotly.express as px
from oracle_database import init_oracle_connection, test_connection
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import Gemini, fallback to simple generator
try:
    from query_generator_gemini import generate_sql_query
    ai_available = True
except ImportError:
    st.warning("Google Gemini not available. Using simple query generator. Install with: `pip install google-generativeai`")
    from simple_query_generator import generate_sql_query
    ai_available = False

# Page configuration
st.set_page_config(
    page_title="Conversational BI Assistant",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 Conversational BI Assistant")
st.markdown("Ask questions about your sales data in plain English and get visualizations!")

# Initialize database connection
@st.cache_resource
def get_connection():
    return init_oracle_connection()

conn = get_connection()

if conn is None:
    st.error("Could not connect to Oracle database. Please check your connection settings.")
    st.stop()

# Test the connection and table
if not test_connection():
    st.error("Sales table not found in the database. Please make sure you've created the table.")
    st.stop()

# Sample questions to get users started
sample_questions = [
    "Show me last 5 sales records",
    "Which product has the highest total sales?",
    "Compare sales between North and South regions",
    "What were the total sales in February 2023?",
    "Show sales by product and region",
    "What is the average sale amount by product?"
]

st.subheader("💡 Try asking something like:")
for question in sample_questions:
    st.markdown(f"- `{question}`")

# Show AI status
if ai_available:
    st.success("✓ AI query generation enabled (using Google Gemini)")
else:
    st.warning("⚠ Using simple query generator. For better results, install: `pip install google-generativeai`")

# Check if Gemini API key is configured
api_key = os.getenv("GEMINI_API_KEY")
if ai_available and (not api_key or api_key == "your_gemini_api_key_here"):
    st.warning("⚠ Gemini API key not configured. Using fallback query generator.")
    st.info("Please add your GEMINI_API_KEY to the .env file")

# User input
query = st.text_input("Ask your question about the sales data:", placeholder="e.g., Show me sales trends for Product X")

if st.button("Generate Results") or query:
    if query:
        with st.spinner("Generating SQL query and fetching results..."):
            # Generate SQL from natural language
            sql_query = generate_sql_query(query)
            
            st.subheader("Generated SQL Query")
            st.code(sql_query, language="sql")
            
            # Check if the SQL query is the generic fallback
            if "ROWNUM <= 5" in sql_query or "ROWNUM <= 10" in sql_query:
                st.info("⚠ Using fallback query. The AI query generator may not be working properly.")
            
            # Execute the query
            try:
                df = pd.read_sql(sql_query, conn)
                
                if not df.empty:
                    st.subheader("Results")
                    st.dataframe(df)
                    
                    # Try to create a visualization
                    if len(df) > 1:  # Only show visualization if we have multiple rows
                        st.subheader("Visualization")
                        
                        # Convert column names to uppercase for consistency
                        df.columns = [col.upper() for col in df.columns]
                        
                        # Check what type of visualization would work best
                        if len(df.columns) == 2 and df.shape[0] > 1:
                            # Likely a bar chart
                            fig = px.bar(df, x=df.columns[0], y=df.columns[1], 
                                        title=f'{df.columns[0]} vs {df.columns[1]}')
                            st.plotly_chart(fig, use_container_width=True)
                        
                        elif 'SALE_DATE' in df.columns and 'AMOUNT' in df.columns:
                            # Time series data - line chart
                            df['SALE_DATE'] = pd.to_datetime(df['SALE_DATE'])
                            df = df.sort_values('SALE_DATE')
                            fig = px.line(df, x='SALE_DATE', y='AMOUNT', title='Sales Over Time')
                            st.plotly_chart(fig, use_container_width=True)
                        
                        elif 'PRODUCT_NAME' in df.columns and 'AMOUNT' in df.columns:
                            # Product comparison - bar chart
                            fig = px.bar(df, x='PRODUCT_NAME', y='AMOUNT', title='Sales by Product')
                            st.plotly_chart(fig, use_container_width=True)
                        
                        elif 'REGION' in df.columns and 'AMOUNT' in df.columns:
                            # Regional data - bar or pie chart
                            col1, col2 = st.columns(2)
                            with col1:
                                fig = px.bar(df, x='REGION', y='AMOUNT', title='Sales by Region')
                                st.plotly_chart(fig, use_container_width=True)
                            with col2:
                                fig = px.pie(df, values='AMOUNT', names='REGION', title='Sales Distribution by Region')
                                st.plotly_chart(fig, use_container_width=True)
                        
                        else:
                            st.info("Data displayed above. Try asking about trends or comparisons for better visualizations.")
                
                else:
                    st.warning("The query returned no results. Try a different question.")
            
            except Exception as e:
                st.error(f"Error executing query: {str(e)}")
                st.info("Try a simpler question or use the manual query tool below.")
    else:
        st.warning("Please enter a question about your data.")

# Add some information about the database
with st.expander("ℹ️ About the database"):
    st.markdown("""
    The database contains a **sales** table with the following columns:
    - `id`: Unique identifier for each sale
    - `product_name`: Name of the product (Product X or Product Y)
    - `sale_date`: Date of the sale
    - `amount`: Sale amount in dollars
    - `region`: Sales region (North or South)
    
    Sample data for January to March 2023 has been pre-loaded.
    """)
    
    # Show sample data
    if st.button("Show Sample Data"):
        sample_df = pd.read_sql("SELECT * FROM sales ORDER BY sale_date FETCH FIRST 5 ROWS ONLY", conn)
        st.dataframe(sample_df)

# Manual query section for testing
with st.expander("🔧 Manual Query Tool"):
    st.markdown("Use this if the AI query generator isn't working properly:")
    
    # Predefined useful queries
    useful_queries = {
        "Show average sale by product": "SELECT product_name, AVG(amount) as average_sale FROM sales GROUP BY product_name ORDER BY average_sale DESC",
        "Show total sales by region": "SELECT region, SUM(amount) as total_sales FROM sales GROUP BY region ORDER BY total_sales DESC",
        "Show sales trend over time": "SELECT sale_date, SUM(amount) as daily_sales FROM sales GROUP BY sale_date ORDER BY sale_date",
        "Show product sales by region": "SELECT product_name, region, SUM(amount) as total_sales FROM sales GROUP BY product_name, region ORDER BY product_name, region",
        "Show last 5 sales": "SELECT * FROM sales ORDER BY sale_date DESC FETCH FIRST 5 ROWS ONLY"
    }
    
    selected_query = st.selectbox("Select a predefined query:", list(useful_queries.keys()))
    manual_query = st.text_area("Or enter your own SQL query:", useful_queries[selected_query])
    
    if st.button("Run Manual Query"):
        try:
            manual_df = pd.read_sql(manual_query, conn)
            st.dataframe(manual_df)
            
            # Try to create a visualization for manual queries too
            if not manual_df.empty and len(manual_df) > 1:
                manual_df.columns = [col.upper() for col in manual_df.columns]
                if 'SALE_DATE' in manual_df.columns and 'AMOUNT' in manual_df.columns:
                    manual_df['SALE_DATE'] = pd.to_datetime(manual_df['SALE_DATE'])
                    manual_df = manual_df.sort_values('SALE_DATE')
                    fig = px.line(manual_df, x='SALE_DATE', y='AMOUNT', title='Sales Over Time')
                    st.plotly_chart(fig, use_container_width=True)
                elif len(manual_df.columns) == 2:
                    fig = px.bar(manual_df, x=manual_df.columns[0], y=manual_df.columns[1], 
                                title=f'{manual_df.columns[0]} vs {manual_df.columns[1]}')
                    st.plotly_chart(fig, use_container_width=True)
                    
        except Exception as e:
            st.error(f"Error: {e}")

# Footer
st.markdown("---")
if ai_available:
    st.markdown("Built with Streamlit, Oracle, and Google Gemini | Conversational BI Assistant")
else:
    st.markdown("Built with Streamlit and Oracle | Conversational BI Assistant")