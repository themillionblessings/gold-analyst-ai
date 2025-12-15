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

engine = GoldAnalystEngine()

from sqlalchemy import text
from backend.database import engine

# ... (existing imports)

@app.get("/")
def read_root():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        db_status = "Connected"
    except Exception as e:
        db_status = f"Disconnected: {str(e)}"
    
    return {"message": "Gold Analyst AI API is running", "database": db_status}

@app.get("/price/{ticker}", response_model=PriceResponse)
def get_price(ticker: str):
    # Currently ignoring ticker and fetching generic gold price as per original logic
    # In future, we can route specifically based on ticker
    data = fetch_gold_price()
    if data and "error" in data:
        raise HTTPException(status_code=500, detail=data["error"])
    return data

@app.get("/news", response_model=List[NewsItem])
def get_news():
    return fetch_market_news()

@app.post("/analyze", response_model=AnalysisResponse)
def analyze_market(request: AnalysisRequest):
    # Helper to construct minimal dicts if full payload isn't provided
    # But since we defined Any in request, we can pass it through if compatible
    # The current engine expects gld_data and xau_data
    
    result = engine.analyze(request.gld_data, request.xau_data)
    
    if result and "rationale_brief" in result:
        return result
    else:
        # Fallback or error handling
        raise HTTPException(status_code=500, detail="Analysis failed to generate valid output")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
