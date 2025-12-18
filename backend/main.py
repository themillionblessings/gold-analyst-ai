from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# Only import simple models at top level
from backend.models import PriceResponse, NewsItem, AnalysisRequest, AnalysisResponse
from typing import List, Dict, Any

app = FastAPI(title="Gold Analyst AI API", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost",
        "https://gold-analyst-frontend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# NOTE: Database engine import moved to read_root to prevent crash if DB is not ready
# but we keep it available for health check if possible, or lazy load it too.
# For maximum safety, we lazy load EVERYTHING.

@app.get("/")
def read_root():
    db_status = "Disconnected"
    try:
        from sqlalchemy import text
        from backend.database import engine as db_engine
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
        # Lazy import
        from backend.services import fetch_gold_price
        
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
    try:
        from backend.services import fetch_market_news
        return fetch_market_news()
    except Exception as e:
        print(f"News Error: {e}")
        return []

@app.post("/analyze", response_model=AnalysisResponse)
def analyze_market(request: AnalysisRequest):
    try:
        from backend.services import GoldAnalystEngine
        ai_engine = GoldAnalystEngine()
        
        result = ai_engine.analyze(request.gld_data, request.xau_data)
        
        if result and "rationale_brief" in result:
            return result
        else:
            raise HTTPException(status_code=500, detail="Analysis failed to generate valid output")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
