from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# Only import simple models at top level
from backend.models import PriceResponse, NewsItem, AnalysisRequest, AnalysisResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

app = FastAPI(title="Gold Analyst AI API", version="2.0.0")

class ValidatedGoldResponse(BaseModel):
    final_price: float = Field(..., description="The audited and verified gold price.")
    source: str = Field(..., description="The data source ultimately used.")
    anomaly_detected: bool = Field(..., description="True if primary source was rejected.")
    system_note: Optional[str] = Field(None, description="Warnings from the Supervisor.")

class GraphIngestRequest(BaseModel):
    text: str = Field(..., description="News text to extract graph entities from.")

@app.get("/api/v1/gold/validated-price", response_model=ValidatedGoldResponse)
async def get_validated_gold_price():
    from backend.services.supervisor import gold_supervisor_app
    initial_state = {"raw_price": None, "is_valid": False, "final_price": None, "source": "unknown", "error": None}
    try:
        final_state = await gold_supervisor_app.ainvoke(initial_state)
        if final_state.get("final_price") is None:
            raise HTTPException(status_code=500, detail="Supervisor failed to secure a valid price.")
        return ValidatedGoldResponse(
            final_price=final_state["final_price"],
            source=final_state["source"],
            anomaly_detected=final_state.get("error") is not None,
            system_note=final_state.get("error")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph Execution Error: {str(e)}")

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

# Persistent Sentiment Engine for caching
sentiment_engine = None

@app.get("/market-mood")
async def get_market_mood():
    global sentiment_engine
    try:
        if sentiment_engine is None:
            from backend.services.sentiment import SentimentEngine
            sentiment_engine = SentimentEngine()
        
        return await sentiment_engine.get_market_mood()
    except Exception as e:
        print(f"Market Mood Endpoint Error: {e}")
        return {"sentiment_score": 50, "mood_label": "Neutral", "key_factors": ["Service temporarily unavailable"]}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_market(request: AnalysisRequest):
    try:
        from backend.services import GoldAnalystEngine
        ai_engine = GoldAnalystEngine()
        
        result = await ai_engine.analyze(request.gld_data, request.xau_data)
        
        if result and "rationale_brief" in result:
            return result
        else:
            raise HTTPException(status_code=500, detail="Analysis failed to generate valid output")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class NewsIngestRequest(BaseModel):
    text: str

@app.post("/api/v1/graph/ingest-news")
async def ingest_news_to_graph(request: NewsIngestRequest):
    from backend.services.graph_rag import KnowledgeGraphService
    kg_service = KnowledgeGraphService()
    try:
        # Call your graph_rag service here
        result = await kg_service.extract_and_store_entities(request.text)
        await kg_service.close()
        
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message"))
            
        return {"status": "success", "nodes_created": result.get("nodes_processed", 0)}
    except Exception as e:
        await kg_service.close()
        raise HTTPException(status_code=500, detail=f"Graph Ingestion Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
