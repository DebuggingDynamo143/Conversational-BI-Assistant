import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def init_postgres_connection():
    """Keep old name for backward compatibility → return SQLAlchemy engine"""
    return get_sqlalchemy_engine()

def get_sqlalchemy_engine():
    """Create and return a SQLAlchemy engine for PostgreSQL (Neon/Cloud)."""
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB")

    if not all([user, password, host, db]):
        raise ValueError("❌ Missing database environment variables. Check your .env file.")

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(url, connect_args={"sslmode": "require"})
    return engine

def test_connection():
    """Check if the sales table exists in PostgreSQL."""
    try:
        engine = get_sqlalchemy_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT to_regclass('public.sales');")
            ).fetchone()
            if result and result[0]:
                print("✅ Sales table exists.")
                return True
            else:
                print("⚠️ Sales table not found.")
                return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def get_db_schema():
    """Fetch schema info for all tables in the current database."""
    try:
        engine = get_sqlalchemy_engine()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name, column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position;
            """)).fetchall()

            schema_dict = {}
            for table, col, dtype in result:
                schema_dict.setdefault(table, []).append(f"{col} {dtype}")

            schema_text = ""
            for table, cols in schema_dict.items():
                schema_text += f"TABLE: {table} ({', '.join(cols)})\n"

            return schema_text.strip()
    except Exception as e:
        return f"⚠️ Error fetching schema: {e}"
