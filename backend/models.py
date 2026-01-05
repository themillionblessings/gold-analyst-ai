from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class PriceResponse(BaseModel):
    asset: str
    price_oz_24k: float
    daily_change_oz: float
    percent_change: str
    rates: Dict[str, float]
    usd: Dict[str, float]
    egypt: Dict[str, float]
    uae: Dict[str, float]

class NewsItem(BaseModel):
    title: str
    link: str
    source: Optional[str] = None
    date: Optional[str] = None

class AnalysisRequest(BaseModel):
    timestamp_utc: Optional[str] = None
    price: float
    change_percent: float
    # We can expand this to accept the full data structure if needed, 
    # but based on the code, it takes gld_data and xau_data dicts.
    # Let's make it flexible to accept the full payload or minimal data.
    gld_data: Dict[str, Any]
    xau_data: Dict[str, Any]

class AnalysisResponse(BaseModel):
    recommendation: str
    confidence: float
    rationale_brief: str
    rationale_technical: str
    suggested_risk_tier: str
    final_action: str
    position_size: str
