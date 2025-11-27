import yfinance as yf
import requests
import os
from datetime import datetime
import yaml

# Load config
try:
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
except:
    config = {}

class YahooProvider:
    def get_latest(self, symbol="GLD"):
        try:
            ticker = yf.Ticker(symbol)
            # Get 2 days to calculate change if needed, but 'history' usually gives OHLC
            data = ticker.history(period="2d")
            
            if data.empty:
                return None
                
            latest = data.iloc[-1]
            prev = data.iloc[-2] if len(data) > 1 else latest
            
            price = float(latest['Close'])
            prev_close = float(prev['Close'])
            pct_change = ((price - prev_close) / prev_close) * 100
            
            return {
                "symbol": symbol,
                "price": price,
                "timestamp_utc": datetime.utcnow().isoformat() + "Z",
                "pct_change_24h": round(pct_change, 2),
                "ohlc": {
                    "open": float(latest['Open']),
                    "high": float(latest['High']),
                    "low": float(latest['Low']),
                    "close": float(latest['Close'])
                }
            }
        except Exception as e:
            print(f"YahooProvider Error: {e}")
            return None

class MetalsApiProvider:
    def __init__(self):
        self.api_key = os.getenv("METALS_API_KEY")
        self.base_url = config.get("providers", {}).get("metals_api_base_url", "https://metals-api.com/api")

    def get_latest(self, symbol="XAU"):
        # If no API key, use Yahoo fallback for XAUUSD (GC=F or XAUUSD=X)
        if not self.api_key:
            return self._get_fallback(symbol)
            
        try:
            # Prototype implementation for Metals-API
            # Note: Real implementation depends on specific endpoint structure
            url = f"{self.base_url}/latest?access_key={self.api_key}&base={symbol}&currencies=USD"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if not data.get("success"):
                return self._get_fallback(symbol)
                
            price = data['rates']['USD']
            # Metals-API might not give OHLC/Change in 'latest' endpoint without paid plan
            # We will estimate or fetch historical if needed. For prototype, we use simple current.
            
            return {
                "symbol": f"{symbol}USD",
                "price": price,
                "timestamp_utc": datetime.utcnow().isoformat() + "Z",
                "pct_change_24h": 0.0, # Placeholder if not available
                "ohlc": {} 
            }
            
        except Exception as e:
            print(f"MetalsApiProvider Error: {e}")
            return self._get_fallback(symbol)

    def _get_fallback(self, symbol):
        """Fallback to Yahoo Finance for Spot Gold proxy if Metals-API fails or no key."""
        # GC=F is Gold Futures, often used as proxy for Spot
        y_sym = "GC=F" 
        provider = YahooProvider()
        data = provider.get_latest(y_sym)
        if data:
            data['symbol'] = f"{symbol}USD (Proxy)"
        return data
