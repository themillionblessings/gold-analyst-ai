# backend/mcp_server.py
from fastmcp import FastMCP
import yfinance as yf
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

# Initialize the standard interface for Agentic AIs
mcp = FastMCP("Gold Analyst MCP")

@mcp.tool()
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def get_live_gold_spot() -> Dict[str, Any]:
    """
    Fetches the live global spot price of Gold (XAU) in USD.
    Returns price per Troy Ounce and calculated price per Gram (24k).
    """
    try:
        # Fetching Gold Futures (GC=F) as a proxy for live spot
        ticker = yf.Ticker("GC=F")
        current_price = ticker.info.get("regularMarketPrice", None)
        
        if not current_price:
            history = ticker.history(period="1d")
            current_price = float(history['Close'].iloc[-1])

        # 1 Troy Ounce = 31.1034768 grams
        price_per_gram_24k = current_price / 31.1034768

        return {
            "status": "success",
            "asset": "Gold (XAU)",
            "currency": "USD",
            "price_per_ounce": round(current_price, 2),
            "price_per_gram_24k": round(price_per_gram_24k, 2)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def calculate_egyptian_gold_premium(spot_usd_per_gram: float, egp_black_market_rate: float, offered_egp_price: float) -> Dict[str, Any]:
    """
    Calculates the premium (%) being charged by an Egyptian gold merchant 
    compared to the global spot price adjusted for the real EGP exchange rate.
    """
    fair_value_egp = spot_usd_per_gram * egp_black_market_rate
    premium_amount = offered_egp_price - fair_value_egp
    
    if fair_value_egp > 0:
        premium_percent = (premium_amount / fair_value_egp) * 100
    else:
        premium_percent = 0.0

    return {
        "fair_value_egp": round(fair_value_egp, 2),
        "offered_price": offered_egp_price,
        "premium_egp": round(premium_amount, 2),
        "premium_percent": round(premium_percent, 2),
        "verdict": "Overpriced" if premium_percent > 5.0 else "Fair Deal"
    }

if __name__ == "__main__":
    # Runs the server using standard stdio communication
    mcp.run()
