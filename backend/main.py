from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# Only import simple models at top level
from backend.models import PriceResponse, NewsItem, AnalysisRequest, AnalysisResponse, RagAskRequest, RagAskResponse
from typing import List, Dict, Any, Optional
from fastapi import File, UploadFile, Depends
from sqlalchemy.orm import Session
from backend.database import get_db

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

# Database initialization
def init_db():
    try:
        from sqlalchemy import text
        from backend.database import engine
        with engine.connect() as conn:
            # Create pgvector extension if we are on Postgres
            if "postgresql" in str(engine.url):
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
                # Create tables
                from backend.database import Base
                import backend.models # Ensure models are loaded
                Base.metadata.create_all(bind=engine)
                print("DEBUG: pgvector extension and tables verified/created")
    except Exception as e:
        print(f"ERROR: Database initialization failed: {e}")

# Run init_db on startup
init_db()

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

# --- RAG Endpoints ---

rag_service = None

@app.post("/rag/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    global rag_service
    try:
        if rag_service is None:
            from backend.services.rag import RagService
            rag_service = RagService()
            
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
            
        try:
            chunks_created = rag_service.ingest_pdf(tmp_path, file.filename, db)
            return {"message": f"Successfully ingested {file.filename}", "chunks": chunks_created}
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    except Exception as e:
        print(f"RAG Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag/ask", response_model=RagAskResponse)
async def ask_question(request: RagAskRequest, db: Session = Depends(get_db)):
    global rag_service
    try:
        if rag_service is None:
            from backend.services.rag import RagService
            rag_service = RagService()
            
        result = rag_service.search_docs(request.question, db)
        return result
    except Exception as e:
        print(f"RAG Ask Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
