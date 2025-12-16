from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.services import GoldAnalystEngine, fetch_gold_price, fetch_market_news
from backend.models import PriceResponse, NewsItem, AnalysisRequest, AnalysisResponse
from typing import List, Dict, Any

app = FastAPI(title="Gold Analyst AI API", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_engine = GoldAnalystEngine()

from sqlalchemy import text
from backend.database import engine as db_engine

# ... (existing imports)

@app.get("/")
def read_root():
    try:
        with db_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        db_status = "Connected"
    except Exception as e:
        db_status = f"Disconnected: {str(e)}"
    
    return {"message": "Gold Analyst AI API is running", "database": db_status}

@app.get("/price/{ticker}")
def get_price(ticker: str):
    from fastapi.responses import JSONResponse
    try:
        data = fetch_gold_price()
        # Validation check manually
        if data and "error" in data:
             # Just return it, don't 500
             return JSONResponse(status_code=500, content={"detail": data["error"]})
        return data
    except Exception as e:
        import traceback
        error_msg = f"Backend Error: {str(e)}"
        print(f"CRITICAL ERROR: {error_msg}\n{traceback.format_exc()}")
        
        # Fallback Data (Safe Mode) to prevent UI crash
        safe_data = {
            "asset": "Gold (Safe Mode)",
            "price_oz_24k": 0.0,
            "daily_change_oz": 0.0,
            "percent_change": "0.0%",
            "rates": {"USD/EGP": 50.0, "USD/AED": 3.67},
            "usd": {"Troy Ounce": 0.0, "24k": 0.0, "21k": 0.0, "18k": 0.0},
            "egypt": {"Troy Ounce": 0.0, "Gold Coin (8g 21k)": 0.0, "24k": 0.0, "21k": 0.0, "18k": 0.0},
            "uae": {"Troy Ounce": 0.0, "24k": 0.0, "21k": 0.0, "18k": 0.0},
            "error_detail": error_msg
        }
        return safe_data

@app.get("/news", response_model=List[NewsItem])
def get_news():
    return fetch_market_news()

@app.post("/analyze", response_model=AnalysisResponse)
def analyze_market(request: AnalysisRequest):
    # Helper to construct minimal dicts if full payload isn't provided
    # But since we defined Any in request, we can pass it through if compatible
    # The current engine expects gld_data and xau_data
    
    result = ai_engine.analyze(request.gld_data, request.xau_data)
    
    if result and "rationale_brief" in result:
        return result
    else:
        # Fallback or error handling
        raise HTTPException(status_code=500, detail="Analysis failed to generate valid output")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
