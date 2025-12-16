import yfinance as yf
from langchain_community.tools import DuckDuckGoSearchRun
import re

def fetch_gold_price():
    """
    Fetches the current market data for Gold.
    Priority 1: Gold Futures (GC=F) via yfinance (most accurate live market proxy).
    Priority 2: Web Search (fallback).
    Returns a dictionary with calculated prices for 24k/oz, 24k/g, and 18k/g.
    """
    current_price_oz = 0
    change_oz = 0
    percent_change = 0
    source = "Market Data"

    # Try 1: Gold Futures (GC=F)
    try:
        spot_ticker = yf.Ticker("GC=F")
        spot_data = spot_ticker.history(period="1d")
        
        if not spot_data.empty:
            current_price_oz = spot_data['Close'].iloc[-1]
            open_price_oz = spot_data['Open'].iloc[-1]
            change_oz = current_price_oz - open_price_oz
            percent_change = (change_oz / open_price_oz) * 100
            source = "Live Futures (GC=F)"
    except Exception:
        pass

    # Try 2: Web Search Fallback (if Futures failed or returned 0)
    if current_price_oz == 0:
        try:
            search = DuckDuckGoSearchRun()
            # Search specifically for the price
            query = "live gold price per ounce usd today"
            results = search.invoke(query)
            
            # Use Regex to find a price pattern like $4,074.79 or 4074.79
            # Looking for large numbers often associated with gold price
            match = re.search(r'\$\s?([0-9,]+\.[0-9]{2})', results)
            if match:
                price_str = match.group(1).replace(',', '')
                current_price_oz = float(price_str)
                source = "Web Search"
                # Estimate change as 0 if we can't parse it
        except Exception:
            pass

    # If all failed, ensure we return a valid structure with 0 values
    if current_price_oz == 0:
        source = "Data Unavailable"
        # We proceed to calculate with 0 so the UI doesn't break

    # Conversions
    # 1 Troy Ounce = 31.1034768 grams
    price_gram_24k_usd = current_price_oz / 31.1034768
    
    # 18k is 75% purity
    price_gram_18k_usd = price_gram_24k_usd * 0.75
    
    # --- Multi-Market Calculations ---
    # Fetch Exchange Rates
    try:
        forex_tickers = yf.Tickers("EGP=X AED=X")
        forex_data = forex_tickers.history(period="1d")
        
        # Get latest rates (fallback to hardcoded estimates if fetch fails to avoid breaking app)
        try:
            rate_egp = forex_data['Close']['EGP=X'].iloc[-1]
        except:
            rate_egp = 50.5 # Fallback estimate
            
        try:
            rate_aed = forex_data['Close']['AED=X'].iloc[-1]
        except:
            rate_aed = 3.67 # Pegged rate
            
    except Exception:
        rate_egp = 50.5
        rate_aed = 3.67

    # Egypt Prices (EGP)
    egp_24k = price_gram_24k_usd * rate_egp
    egp_21k = egp_24k * (21/24)
    egp_18k = egp_24k * (18/24)
    egp_ounce = current_price_oz * rate_egp
    egp_coin = egp_21k * 8 # Standard Gold Coin is 8g of 21k
    
    # UAE Prices (AED)
    aed_24k = price_gram_24k_usd * rate_aed
    aed_21k = aed_24k * (21/24)
    aed_18k = aed_24k * (18/24)
    aed_ounce = current_price_oz * rate_aed
    
    # International Prices (USD)
    usd_24k = price_gram_24k_usd
    usd_21k = usd_24k * (21/24)
    usd_18k = usd_24k * (18/24)
    usd_ounce = current_price_oz
    
    return {
        "asset": f"Gold ({source})",
        "price_oz_24k": round(current_price_oz, 2),
        "daily_change_oz": round(change_oz, 2),
        "percent_change": f"{round(percent_change, 2)}%",
        "rates": {"USD/EGP": round(rate_egp, 2), "USD/AED": round(rate_aed, 2)},
        "usd": {
            "Troy Ounce": round(usd_ounce, 2),
            "24k": round(usd_24k, 2),
            "21k": round(usd_21k, 2),
            "18k": round(usd_18k, 2)
        },
        "egypt": {
            "Troy Ounce": round(egp_ounce, 2),
            "Gold Coin (8g 21k)": round(egp_coin, 2),
            "24k": round(egp_24k, 2),
            "21k": round(egp_21k, 2),
            "18k": round(egp_18k, 2)
        },
        "uae": {
            "Troy Ounce": round(aed_ounce, 2),
            "24k": round(aed_24k, 2),
            "21k": round(aed_21k, 2),
            "18k": round(aed_18k, 2)
        }
    }

def fetch_market_news(query="Gold price analysis market news today"):
    """
    Searches for the latest market news using DuckDuckGo.
    Returns a list of dictionaries with 'title', 'link', and 'source'.
    """
    try:
        from duckduckgo_search import DDGS
        news_list = []
        with DDGS() as ddgs:
            # Get 5 news results
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

def fetch_historical_data(period="max"):
    """
    Fetches historical gold price data suitable for plotting.
    Defaults to 'max' to get data from as far back as possible (or year 2000).
    Returns a DataFrame with Date and Close columns.
    """
    try:
        # Use GC=F for futures history if available, else GLD
        ticker = yf.Ticker("GC=F")
        data = ticker.history(start="2000-01-01")
        
        if data.empty:
            ticker = yf.Ticker("GLD")
            data = ticker.history(start="2000-01-01")
            # Scale GLD to approx spot price if using GLD
            data['Close'] = data['Close'] * 10.65
            
        return data[['Close']]
    except Exception as e:
        return None

if __name__ == "__main__":
    # Simple test
    print("Price:", fetch_gold_price())
    print("News:", fetch_market_news()[:100] + "...")
