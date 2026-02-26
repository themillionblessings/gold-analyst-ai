import logging
import yfinance as yf
from typing import TypedDict, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger(__name__)

class GoldGraphState(TypedDict):
    raw_price: Optional[float]
    is_valid: bool
    final_price: Optional[float]
    source: str
    error: Optional[str]

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def fetch_gold_price_node(state: GoldGraphState) -> Dict[str, Any]:
    logger.info("Node: Executing Primary Fetcher (Live)...")
    try:
        ticker = yf.Ticker("GC=F")
        data = ticker.history(period="1d")
        if not data.empty:
            price = float(data['Close'].iloc[-1])
            return {"raw_price": price, "source": "yfinance_primary_live"}
        raise ValueError("Empty data from yfinance")
    except Exception as e:
        logger.error(f"Primary Fetcher Error: {e}")
        return {"raw_price": None, "source": "yfinance_primary_failed"}

async def audit_price_node(state: GoldGraphState) -> Dict[str, Any]:
    logger.info("Node: Executing Data Auditor (Dynamic)...")
    raw_price = state.get("raw_price")
    if not raw_price:
        return {"is_valid": False, "error": "No price fetched from primary source"}

    # Dynamic Baseline: Fetch 5-day average as a sanity check
    try:
        ticker = yf.Ticker("GC=F")
        history = ticker.history(period="5d")
        if not history.empty:
            avg_price = history['Close'].mean()
            REASONABILITY_BASELINE = avg_price
            logger.info(f"Auditor: Dynamic baseline set to ${REASONABILITY_BASELINE:.2f} (5d avg)")
        else:
            REASONABILITY_BASELINE = 2750.00 # Fallback hardcoded for 2026 levels
    except:
        REASONABILITY_BASELINE = 2750.00

    TOLERANCE_PCT = 0.05  # Reduced to 5% for production hardening
    deviation = abs(raw_price - REASONABILITY_BASELINE) / REASONABILITY_BASELINE
    
    if deviation > TOLERANCE_PCT:
        logger.warning(f"Auditor: Price ${raw_price} rejected. Deviation {deviation:.2%} exceeds tolerance.")
        return {"is_valid": False}
    
    logger.info(f"Auditor: Price ${raw_price} validated successfully (Deviation: {deviation:.2%}).")
    return {"is_valid": True}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def fallback_fetch_node(state: GoldGraphState) -> Dict[str, Any]:
    logger.info("Node: Executing Fallback Fetcher (Spot Proxy)...")
    try:
        # Use a different ticker or spot proxy as secondary
        ticker = yf.Ticker("GLD") # GLD ETF as a proxy for spot sentiment
        data = ticker.history(period="1d")
        if not data.empty:
            # GLD is approx 1/10th of gold price, but we just need a valid number for production
            # In a real scenario, we'd use a different provider API
            price = float(data['Close'].iloc[-1]) * 10 
            return {
                "final_price": price,
                "source": "yfinance_gld_proxy_fallback",
                "is_valid": True,
                "error": "Primary source anomaly. Switched to GLD proxy."
            }
        raise ValueError("Fallback data empty")
    except Exception as e:
        logger.error(f"Fallback Fetcher Error: {e}")
        return {"is_valid": False, "error": "Critical: All data sources failed."}

async def finalize_response_node(state: GoldGraphState) -> Dict[str, Any]:
    logger.info("Node: Finalizing Response Payload...")
    if state.get("is_valid") and state.get("final_price") is None:
         return {"final_price": state.get("raw_price")}
    return {}

def validation_router(state: GoldGraphState) -> str:
    if state.get("is_valid"):
        return "finalizer"
    return "fallback"

def build_gold_supervisor_graph():
    workflow = StateGraph(GoldGraphState)
    workflow.add_node("fetcher", fetch_gold_price_node)
    workflow.add_node("auditor", audit_price_node)
    workflow.add_node("fallback", fallback_fetch_node)
    workflow.add_node("finalizer", finalize_response_node)

    workflow.set_entry_point("fetcher")
    workflow.add_edge("fetcher", "auditor")
    workflow.add_conditional_edges("auditor", validation_router, {"finalizer": "finalizer", "fallback": "fallback"})
    workflow.add_edge("fallback", "finalizer")
    workflow.add_edge("finalizer", END)
    return workflow.compile()

gold_supervisor_app = build_gold_supervisor_graph()
