import sqlite3
import json
import yaml
from datetime import datetime, timedelta
from .data_provider import YahooProvider

DB_NAME = "gold_analyst.db"

# Load config
try:
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
except:
    config = {}

class Evaluator:
    def __init__(self):
        self.provider = YahooProvider()
        self.success_threshold = config.get("evaluation", {}).get("success_threshold_pct", 0.2) / 100.0

    def run_evaluation(self):
        """
        Iterates through pending predictions and checks if outcomes are realized.
        Updates the DB.
        """
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get predictions that haven't been fully evaluated
        # For simplicity, we check all recent ones that have null outcomes
        cursor.execute("SELECT * FROM predictions WHERE horizon_1d_outcome IS NULL")
        rows = cursor.fetchall()
        
        current_price_data = self.provider.get_latest("GLD")
        if not current_price_data:
            conn.close()
            return "Could not fetch current price for evaluation."
            
        current_price = current_price_data['price']
        current_time = datetime.utcnow()
        
        updated_count = 0
        
        for row in rows:
            pred_time = datetime.fromisoformat(row['timestamp_utc'].replace("Z", ""))
            age = current_time - pred_time
            
            # Check 1 Day Horizon (approx 24h)
            if age > timedelta(hours=24) and row['horizon_1d_outcome'] is None:
                outcome = self._evaluate_outcome(row, current_price)
                cursor.execute("UPDATE predictions SET horizon_1d_outcome = ? WHERE id = ?", (outcome, row['id']))
                updated_count += 1
                
            # Logic for 7d and 30d can be added similarly
            
        conn.commit()
        conn.close()
        return f"Evaluated {updated_count} predictions."

    def _evaluate_outcome(self, row, current_price):
        entry_price = row['gld_price']
        model_out = json.loads(row['model_output_json'])
        action = model_out.get("final_action", "HOLD")
        
        pct_change = (current_price - entry_price) / entry_price
        
        if action == "BUY":
            return "SUCCESS" if pct_change >= self.success_threshold else "FAILURE"
        elif action == "SELL":
            return "SUCCESS" if pct_change <= -self.success_threshold else "FAILURE"
        else: # HOLD
            return "SUCCESS" if abs(pct_change) < self.success_threshold else "FAILURE"

    def get_metrics(self):
        """Computes Accuracy and Brier Score."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("SELECT horizon_1d_outcome, model_output_json FROM predictions WHERE horizon_1d_outcome IS NOT NULL")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {"accuracy": 0.0, "brier_score": 0.0, "count": 0}
            
        success_count = 0
        brier_sum = 0
        
        for outcome, output_json in rows:
            if outcome == "SUCCESS":
                success_count += 1
                
            # Brier Score Calculation (Simplified)
            # Outcome: 1 if Success, 0 if Failure
            # Probability: Confidence / 100
            data = json.loads(output_json)
            prob = float(data.get("confidence", 50)) / 100.0
            actual = 1.0 if outcome == "SUCCESS" else 0.0
            brier_sum += (prob - actual) ** 2
            
        accuracy = (success_count / len(rows)) * 100
        brier_score = brier_sum / len(rows)
        
        return {
            "accuracy": round(accuracy, 1),
            "brier_score": round(brier_score, 3),
            "count": len(rows)
        }
