# Gold Analyst AI - Application Specification Sheet

**Version:** 1.0.0
**Date:** December 10, 2025
**Status:** MVP / Functional Prototype

---

## 1. Project Overview
**Gold Analyst AI** is a specialized real-time financial dashboard designed to assist investors in making informed decisions about gold and silver markets. It combines real-time market data with an autonomous AI agent to generate actionable "Buy", "Hold", or "Sell" recommendations.

**Core Value Proposition:**
- Real-time aggregation of precious metal prices across global currencies (USD, EGP, AED, SAR, INR).
- AI-driven market analysis using Google's Gemini models.
- "Apple-Style" premium UI/UX for specific clarity and minimalist aesthetics.

---

## 2. Technology Stack

### Backend & Core Logic
- **Language:** Python 3.14
- **AI Engine:** Google Gemini (via `google-generativeai` SDK).
- **Data Processing:** Pandas, NumPy.
- **Database:** SQLite (local storage for logging predictions and analysis history).

### Frontend & UI
- **Framework:** Streamlit.
- **Visualization:** Plotly (Interactive financial charts).
- **Styling:** Custom CSS injections matching strict Apple Design System tokens (San Francisco font stack, specific hex/HSL palettes).

### Data Integrations
- **Market Data:**
    - `yfinance` (Yahoo Finance API) for live ticker data.
    - Custom web scrapers/APIs (extensible structure in `data_provider.py`).
- **News:** DuckDuckGo Search (via `ddgs`) for real-time market news.

### DevOps & Tooling
- **Version Control:** Git.
- **Environment Management:** `venv`, `.env` for secrets.
- **Testing:** `pytest` for unit testing core logic.
- **CI/CD:** GitHub Actions (basic CI workflow for tests).

---

## 3. System Architecture

```mermaid
graph TD
    User[End User] --> UI[Streamlit Frontend]
    UI --> AppLogic[app.py Orchestrator]
    
    subgraph Core Services
        AppLogic --> DP[Data Provider Service]
        AppLogic --> AI[AI Analysis Engine]
        AppLogic --> Calc[Calculator Tools]
    end
    
    subgraph External APIs
        DP --> Yahoo[Yahoo Finance]
        DP --> Metals[Metals API (Optional)]
        AI --> Gemini[Google Gemini API]
        DP --> Search[Web Search / News]
    end
    
    subgraph Storage
        AI --> DB[(SQLite Database)]
        DB --> Logger[Audit Logs / History]
    end
```

---

## 4. Feature Specifications

### A. Dashboard & Visualization
- **Hero Section:** Large, high-impact display of current XAU/USD price with color-coded delta changes.
- **Global Markets:** Live price tracking for EGP, AED, SAR, and INR converted from live exchange rates.
- **Interactive Charts:** 
    - 6-Month historical trend line.
    - Sparkline charts for quick trend visualization.

### B. AI Analysis Agent
- **Role:** Acts as a senior financial analyst.
- **Input:** Current price, moving averages, recent news headlines, historical volatility.
- **Output:**
    - **Decision:** BUY / SELL / HOLD.
    - **Confidence Score:** 1-10 rating.
    - **Reasoning:** Bulleted list of fundamental and technical factors.
- **Latency:** ~2-5 seconds per analysis generation.

### C. Utilities
- **Gold Value Calculator:**
    - Inputs: Weight (grams), Karat (24K, 21K, 18K), Market (USD, EGP, AED).
    - Outputs: Estimated sell value based on live market spot prices.
- **News Feed:** Curated card view of top 3 recent market-moving news stories.

---

## 5. Design System Tokens (Apple-Inspired)

The UI enforces a strict design system via `app.py` CSS injection:

- **Color Palette:**
    - `Background`: `#FFFFFF` (Primary), `#F5F5F7` (Secondary/Sidebar).
    - `Text`: `#0B0B0C` (Primary), `#6E6E73` (Secondary).
    - `Accents`: `#007AFF` (Blue), `#12A851` (Green/Buy), `#D93025` (Red/Sell).
    - **Dark Mode Components:** Input fields and Dropdowns force `#1c1c1e` background with `#FFFFFF` text for contrast.
- **Typography:** System fonts (`SF Pro`), strict hierarchy (Hero > Title > Subtitle > Body).
- **Components:**
    - Cards with subtle shadows (`0px 4px 12px rgba(0,0,0,0.05)`).
    - Buttons with soft grey backgrounds (`#E5E5EA`) and scale transformations on hover.

---

## 6. Review Requests for Gemini 3 Pro (Roadmap)

**We are seeking review and improvements on the following:**

1.  **Production Readiness:**
    - Transition strategy from Streamlit (prototyping) to a more robust frontend (e.g., Next.js/React) backed by FastAPI.
    - Strategies for containerization (Docker) and cloud deployment (e.g., Cloud Run, AWS).
2.  **AI Enhancements:**
    - Implementing "Chain of Thought" reasoning for deeper analysis.
    - Adding multi-modal capabilities (analyzing chart images directly).
3.  **Data Reliability:**
    - Implementing caching strategies (Redis) to reduce API calls and improve load speeds.
    - Backup data providers for redundancy.
4.  **Feature Expansion:**
    - User Authentication (saved portfolios).
    - Price Alerts (Push notifications/Emails).
    - Technical Analysis indicators (RSI, MACD, Bollinger Bands) computed server-side.

---
**Repository Structure:**
- `/src`: Core business logic (AI, Data, Logging).
- `/tests`: Unit tests.
- `app.py`: Main entry point.
- `requirements.txt`: Dependencies.
