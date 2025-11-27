import sqlite3
import os

DB_NAME = "gold_analyst.db"

def migrate():
    """Creates the necessary tables for the Gold Analyst app."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create predictions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id TEXT PRIMARY KEY,
        timestamp_utc TEXT,
        gld_price REAL,
        xau_price REAL,
        input_json TEXT,
        model_output_json TEXT,
        horizon_1d_outcome TEXT,
        horizon_7d_outcome TEXT,
        horizon_30d_outcome TEXT
    )
    """)
    
    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' migrated successfully.")

if __name__ == "__main__":
    migrate()
