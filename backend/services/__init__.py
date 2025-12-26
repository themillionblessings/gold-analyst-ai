import os
import json
import yaml
import yfinance as yf
import re
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from duckduckgo_search import DDGS

# Load config (assuming config.yaml is in the root or backend root, will handle path later)
# For now, let's look for it in the parent directory or current directory
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml") 
if not os.path.exists(CONFIG_PATH):
    CONFIG_PATH = "config.yaml"

try:
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
except:
    config = {}

import google.generativeai as genai

# ... imports ...

class GoldAnalystEngine:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model_name = "gemini-flash-latest"
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={"temperature": 0.0, "response_mime_type": "application/json"}
            )
        else:
            self.model = None
        
    def analyze(self, gld_data: Dict[str, Any], xau_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.model:
            return self._mock_response("Error: Missing GOOGLE_API_KEY")
            
        input_payload = {
            "timestamp_utc": gld_data.get("timestamp_utc"),
            "assets": {
                "GLD": gld_data,
                "XAU": xau_data
            },
            "derived": {
                "recent_trend_slope": 0.0,
                "short_volatility": 0.0,
                "notes": "Analyze based on price action and technicals."
            },
            "config": {
                "risk_tiers": list(config.get("risk_tiers", {}).keys()),
                "mapping_thresholds": config.get("mapping_thresholds", {})
            }
        }
        
        system_prompt = """
        You are an expert Gold Analyst AI.
        Your task is to provide ultra-minimal Buy/Hold/Sell recommendations for Gold.
        Tone: Ultra-minimal, direct, professional.
        Output: STRICT JSON only.
        Required Output Schema:
        {
          "recommendation": "BUY|HOLD|SELL",
          "confidence": <float 0-100>,
          "rationale_brief": "One-line ultra-minimal explanation (max 20 words)",
          "rationale_technical": "One short paragraph technical rationale (max 80 words)",
          "suggested_risk_tier": "Conservative|Moderate|Aggressive"
        }
        """
        
        user_prompt = f"Analyze this market data:\n{json.dumps(input_payload, indent=2)}"
        
        try:
            # Native API call
            # Combine system and user prompt effectively or use system_instruction if available in newer lib
            # check if system_instruction is supported, otherwise prepend
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = self.model.generate_content(full_prompt)
            content = response.text.strip()
            
            # Clean up standard markdown json
            if content.startswith("```json"): content = content[7:]
            if content.endswith("```"): content = content[:-3]
            
            output_json = json.loads(content.strip())
            
            final_recommendation = self._map_recommendation(output_json)
            output_json["final_action"] = final_recommendation
            output_json["position_size"] = self._get_position_size(output_json.get("suggested_risk_tier"))
            
            return output_json
            
        except Exception as e:
            return self._mock_response(f"AI Error: {str(e)}")

    def _map_recommendation(self, output_json):
        rec = output_json.get("recommendation", "HOLD").upper()
        conf = float(output_json.get("confidence", 0))
        thresholds = config.get("mapping_thresholds", {"confidence_buy": 60, "confidence_sell": 60})
        if rec == "BUY" and conf >= thresholds["confidence_buy"]: return "BUY"
        elif rec == "SELL" and conf >= thresholds["confidence_sell"]: return "SELL"
        else: return "HOLD"

    def _get_position_size(self, tier):
        return config.get("risk_tiers", {}).get(tier, "0.0%")

    def _mock_response(self, error_msg):
        return {
            "recommendation": "HOLD",
            "confidence": 0,
            "rationale_brief": error_msg,
            "rationale_technical": "System error.",
            "suggested_risk_tier": "Conservative",
            "final_action": "HOLD",
            "position_size": "0.0%"
        }

def fetch_gold_price() -> Dict[str, Any]:
    current_price_oz = 0
    change_oz = 0
    percent_change = 0
    source = "Market Data"

    try:
        spot_ticker = yf.Ticker("GC=F")
        spot_data = spot_ticker.history(period="1d")
        
        # Fallback for weekends/holidays if 1d is empty
        if spot_data.empty:
            spot_data = spot_ticker.history(period="5d")
            
        if not spot_data.empty:
            current_price_oz = spot_data['Close'].iloc[-1]
            open_price_oz = spot_data['Open'].iloc[-1] if len(spot_data) > 0 else current_price_oz
            change_oz = current_price_oz - open_price_oz
            percent_change = (change_oz / open_price_oz) * 100 if open_price_oz != 0 else 0
            source = "Live Futures (GC=F)"
    except Exception as e:
        print(f"Error fetching gold price: {e}")
        pass

    if current_price_oz == 0:
        # Fallback logic simplified for backend (could invoke separate tools if needed)
        # For simplicity, returning empty/zero if primary fails, similar to updated tools.py
        pass

    if current_price_oz == 0:
        source = "Data Unavailable"
        # Proceed with 0

    price_gram_24k_usd = current_price_oz / 31.1034768
    price_gram_18k_usd = price_gram_24k_usd * 0.75
    
    # Forex
    try:
        forex_tickers = yf.Tickers("EGP=X AED=X")
        forex_data = forex_tickers.history(period="1d")
        
        # Fallback for weekends
        if forex_data.empty:
            forex_data = forex_tickers.history(period="5d")
            
        if not forex_data.empty:
            rate_egp = forex_data['Close']['EGP=X'].iloc[-1]
            rate_aed = forex_data['Close']['AED=X'].iloc[-1]
        else:
            rate_egp = 50.5
            rate_aed = 3.67
    except Exception as e:
        print(f"Error fetching forex rates: {e}")
        rate_egp = 50.5
        rate_aed = 3.67

    return {
        "asset": f"Gold ({source})",
        "price_oz_24k": round(current_price_oz, 2),
        "daily_change_oz": round(change_oz, 2),
        "percent_change": f"{round(percent_change, 2)}%",
        "rates": {"USD/EGP": round(rate_egp, 2), "USD/AED": round(rate_aed, 2)},
        "usd": {
            "Troy Ounce": round(current_price_oz, 2),
            "24k": round(price_gram_24k_usd, 2),
            "21k": round(price_gram_24k_usd * (21/24), 2),
            "18k": round(price_gram_18k_usd, 2)
        },
        "egypt": {
            "Troy Ounce": round(current_price_oz * rate_egp, 2),
            "Gold Coin (8g 21k)": round(price_gram_24k_usd * rate_egp * (21/24) * 8, 2),
            "24k": round(price_gram_24k_usd * rate_egp, 2),
            "21k": round(price_gram_24k_usd * rate_egp * (21/24), 2),
            "18k": round(price_gram_18k_usd * rate_egp, 2)
        },
        "uae": {
            "Troy Ounce": round(current_price_oz * rate_aed, 2),
            "24k": round(price_gram_24k_usd * rate_aed, 2),
            "21k": round(price_gram_24k_usd * rate_aed * (21/24), 2),
            "18k": round(price_gram_18k_usd * rate_aed, 2)
        }
    }

def fetch_market_news(query="Gold price analysis market news today") -> List[Dict[str, Any]]:
    try:
        news_list = []
        with DDGS() as ddgs:
            ddgs_news = list(ddgs.news(keywords=query, max_results=5))
            for item in ddgs_news:
                news_list.append({
                    "title": item.get("title"),
                    "link": item.get("url"),
                    "source": item.get("source"),
                    "date": item.get("date")
                })
        return news_list
    except Exception as e:
        return [{"title": "News Unavailable", "source": "System", "link": "#", "error": str(e)}]
