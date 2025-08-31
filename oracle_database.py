import oracledb
import os
from dotenv import load_dotenv

# Try to initialize thick mode (for local development)
try:
    oracledb.init_oracle_client()
except Exception as e:
    print(f"Thick mode initialization warning: {e}")
    print("Falling back to thin mode...")

load_dotenv()

def init_oracle_connection():
    try:
        # Get connection parameters from environment variables
        user = os.getenv("ORACLE_USER")
        password = os.getenv("ORACLE_PASSWORD")
        dsn = os.getenv("ORACLE_DSN")
        
        # For Streamlit Cloud deployment, check secrets
        if not all([user, password, dsn]):
            try:
                import streamlit as st
                user = st.secrets.get("ORACLE_USER")
                password = st.secrets.get("ORACLE_PASSWORD")
                dsn = st.secrets.get("ORACLE_DSN")
            except:
                pass
        
        if not all([user, password, dsn]):
            print("Missing database connection parameters")
            print("Please set ORACLE_USER, ORACLE_PASSWORD, and ORACLE_DSN environment variables")
            return None
        
        # Oracle connection details - use thin mode for compatibility
        connection = oracledb.connect(
            user=user,
            password=password,
            dsn=dsn
        )
        print("Successfully connected to Oracle database!")
        return connection
    except Exception as e:
        print(f"Error connecting to Oracle: {e}")
        return None

def test_connection():
    """Test the database connection and verify the sales table exists"""
    conn = init_oracle_connection()
    if conn is None:
        print("Failed to connect to Oracle database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if sales table exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM user_tables 
            WHERE table_name = UPPER('sales')
        """)
        table_exists = cursor.fetchone()[0] > 0
        
        if table_exists:
            print("Sales table exists!")
            
            # Check data in sales table
            cursor.execute("SELECT COUNT(*) FROM sales")
            row_count = cursor.fetchone()[0]
            print(f"Sales table has {row_count} rows")
            
            # Show a sample of the data
            cursor.execute("SELECT * FROM sales WHERE ROWNUM <= 5")
            sample_data = cursor.fetchall()
            print("Sample data:")
            for row in sample_data:
                print(row)
        else:
            print("Sales table does not exist!")
            
        cursor.close()
        return table_exists
        
    except Exception as e:
        print(f"Error testing connection: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    test_connection()
