import sqlite3
import uuid
from datetime import datetime
import json

DB_NAME = "gold_analyst.db"

def log_prediction(gld_price, xau_price, input_data, model_output):
    """
    Logs a new prediction to the database.
    Returns the prediction ID.
    """
    prediction_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO predictions (
        id, timestamp_utc, gld_price, xau_price, input_json, model_output_json
    ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        prediction_id,
        timestamp,
        gld_price,
        xau_price,
        json.dumps(input_data),
        json.dumps(model_output)
    ))
    
    conn.commit()
    conn.close()
    return prediction_id

def get_recent_predictions(limit=10):
    """Fetches recent predictions for display or evaluation."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM predictions ORDER BY timestamp_utc DESC LIMIT ?", (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return rows
