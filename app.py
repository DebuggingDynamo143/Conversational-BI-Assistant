import streamlit as st
import pandas as pd
import plotly.express as px
from postgresql_database import init_postgres_connection, test_connection
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import Gemini, fallback to simple generator
try:
    from query_generator_gemini import generate_sql_query
    ai_available = True
except ImportError:
    st.warning("Google Gemini not available. Using simple query generator.")
    from simple_query_generator import generate_sql_query
    ai_available = False

# Page configuration
st.set_page_config(
    page_title="Conversational BI Assistant",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Conversational BI Assistant")
st.markdown("Ask questions about your sales data in plain English and get visualizations!")

# Initialize database connection
@st.cache_resource
def get_connection():
    return init_postgres_connection()

engine = get_connection()

if engine is None:
    st.error("Could not connect to PostgreSQL database. Please check your connection settings.")
    st.stop()

# Test the connection
if not test_connection():
    st.error("Sales table not found in the database. Please create it before proceeding.")
    st.stop()

# Sample questions
sample_questions = [
    "Show me last 5 sales records",
    "Which product has the highest total sales?",
    "Compare sales between North and South regions",
    "What were the total sales in February 2025?",
    "Show sales by product and region",
    "What is the average sale amount by product?"
]

st.subheader("💡 Try asking something like:")
for question in sample_questions:
    st.markdown(f"- `{question}`")

# AI status
if ai_available:
    st.success("✓ AI query generation enabled (Gemini)")
else:
    st.warning("⚠ Using simple query generator.")

query = st.text_input("Ask your question about the sales data:", placeholder="e.g., Show me sales trends for Product X")

if st.button("Generate Results") or query:
    if query:
        with st.spinner("Generating SQL query and fetching results..."):
            sql_query = generate_sql_query(query)
            st.subheader("Generated SQL Query")
            st.code(sql_query, language="sql")

            try:
                df = pd.read_sql(sql_query, engine)

                if not df.empty:
                    st.subheader("Results")
                    st.dataframe(df)

                    if len(df) > 1:
                        st.subheader("Visualization")
                        df.columns = [col.upper() for col in df.columns]

                        if len(df.columns) == 2 and df.shape[0] > 1:
                            fig = px.bar(df, x=df.columns[0], y=df.columns[1])
                            st.plotly_chart(fig, use_container_width=True)

                        elif 'SALE_DATE' in df.columns and 'AMOUNT' in df.columns:
                            df['SALE_DATE'] = pd.to_datetime(df['SALE_DATE'])
                            df = df.sort_values('SALE_DATE')
                            fig = px.line(df, x='SALE_DATE', y='AMOUNT', title='Sales Over Time')
                            st.plotly_chart(fig, use_container_width=True)

                        elif 'PRODUCT_NAME' in df.columns and 'AMOUNT' in df.columns:
                            fig = px.bar(df, x='PRODUCT_NAME', y='AMOUNT', title='Sales by Product')
                            st.plotly_chart(fig, use_container_width=True)

                        elif 'REGION' in df.columns and 'AMOUNT' in df.columns:
                            col1, col2 = st.columns(2)
                            with col1:
                                fig = px.bar(df, x='REGION', y='AMOUNT', title='Sales by Region')
                                st.plotly_chart(fig, use_container_width=True)
                            with col2:
                                fig = px.pie(df, values='AMOUNT', names='REGION', title='Sales Distribution by Region')
                                st.plotly_chart(fig, use_container_width=True)

                else:
                    st.warning("The query returned no results.")
            except Exception as e:
                st.error(f"Error executing query: {str(e)}")
    else:
        st.warning("Please enter a question about your data.")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit, PostgreSQL, and Google Gemini | Conversational BI Assistant")
