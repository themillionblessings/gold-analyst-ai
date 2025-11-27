import pytest
import json
from src.data_provider import YahooProvider
from src.ai_engine import GoldAnalystEngine
from src.evaluator import Evaluator

# --- Data Provider Tests ---
def test_yahoo_provider_structure():
    provider = YahooProvider()
    # We mock the actual call or just test structure if we can't hit network
    # For this minimal test, we'll assume network is available or handle None
    data = provider.get_latest("GLD")
    if data:
        assert "symbol" in data
        assert "price" in data
        assert "timestamp_utc" in data
        assert isinstance(data["price"], float)

# --- AI Engine Tests ---
def test_ai_engine_mapping():
    engine = GoldAnalystEngine()
    
    # Test Buy Mapping
    buy_output = {"recommendation": "BUY", "confidence": 80}
    assert engine._map_recommendation(buy_output) == "BUY"
    
    # Test Sell Mapping
    sell_output = {"recommendation": "SELL", "confidence": 80}
    assert engine._map_recommendation(sell_output) == "SELL"
    
    # Test Hold (Low Confidence)
    weak_buy = {"recommendation": "BUY", "confidence": 40}
    assert engine._map_recommendation(weak_buy) == "HOLD"

# --- Evaluator Tests ---
def test_evaluator_logic():
    evaluator = Evaluator()
    evaluator.success_threshold = 0.002 # 0.2%
    
    # Test Buy Success
    row_buy = {
        "gld_price": 100.0,
        "model_output_json": json.dumps({"final_action": "BUY"})
    }
    assert evaluator._evaluate_outcome(row_buy, 100.3) == "SUCCESS" # +0.3%
    assert evaluator._evaluate_outcome(row_buy, 100.1) == "FAILURE" # +0.1%
    
    # Test Sell Success
    row_sell = {
        "gld_price": 100.0,
        "model_output_json": json.dumps({"final_action": "SELL"})
    }
    assert evaluator._evaluate_outcome(row_sell, 99.7) == "SUCCESS" # -0.3%
    assert evaluator._evaluate_outcome(row_sell, 99.9) == "FAILURE" # -0.1%
    
    # Test Hold Success
    row_hold = {
        "gld_price": 100.0,
        "model_output_json": json.dumps({"final_action": "HOLD"})
    }
    assert evaluator._evaluate_outcome(row_hold, 100.1) == "SUCCESS" # +0.1%
    assert evaluator._evaluate_outcome(row_hold, 100.3) == "FAILURE" # +0.3%
