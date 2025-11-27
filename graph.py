from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from tools import fetch_gold_price, fetch_market_news

# Define the state of our workflow
class AgentState(TypedDict):
    gold_data: Optional[dict]
    market_news: Optional[str]
    analysis: Optional[str]

# Node 1: Fetch Data
def fetch_data_node(state: AgentState):
    print("--- Fetching Data ---")
    price_data = fetch_gold_price()
    news_data = fetch_market_news(query="Gold price analysis market news today")
    
    return {
        "gold_data": price_data,
        "market_news": news_data
    }

# Node 2: Analyze Data (LLM)
def analyze_node(state: AgentState):
    print("--- Analyzing Data ---")
    
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        return {"analysis": "Error: GOOGLE_API_KEY not found in environment variables."}
        
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-09-2025")
    
    gold_data = state["gold_data"]
    news = state["market_news"]
    
    # Format news for LLM
    news_text = ""
    if isinstance(news, list):
        for item in news:
            news_text += f"- {item.get('title')} ({item.get('source')})\n"
    else:
        news_text = str(news)
    
    prompt = f"""
    You are an expert financial analyst specializing in commodities.
    
    Here is the latest data for Gold (GLD ETF):
    {gold_data}
    
    Here is the latest market news headlines:
    {news_text}
    
    Based on this, provide a concise analysis:
    1. Current Trend (Bullish/Bearish/Neutral)
    2. Key Drivers (from news)
    3. Recommendation (Buy/Sell/Hold) with confidence level.
    
    Keep it professional and actionable.
    """
    
    messages = [
        SystemMessage(content="You are a senior commodities analyst."),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    # Return both analysis AND the original news list for the UI
    return {"analysis": response.content, "market_news": news}

# Build the Graph
workflow = StateGraph(AgentState)

workflow.add_node("fetcher", fetch_data_node)
workflow.add_node("analyst", analyze_node)

workflow.set_entry_point("fetcher")
workflow.add_edge("fetcher", "analyst")
workflow.add_edge("analyst", END)

app = workflow.compile()
