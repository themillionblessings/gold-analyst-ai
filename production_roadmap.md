# Production Roadmap: Gold Analyst AI v2.0

## Phase 1: Architecture Overhaul (Headless Architecture)
**Objective:** Decouple Frontend and Backend to achieve "Apple-style" quality and scalability.

- [ ] **Backend (FastAPI)**
    - [ ] Initialize new `backend/` directory with `FastAPI`.
    - [ ] Create REST endpoints for `/market-data`, `/financial-analysis`, and `/calculator`.
    - [ ] Port `src/ai_engine.py` logic to asynchronous service.
    - [ ] Port `src/data_provider.py` to service layer.
- [ ] **Frontend (Next.js)**
    - [ ] Initialize `frontend/` directory with Next.js & Tailwind CSS.
    - [ ] Implement Apple Design System tokens in `tailwind.config.js`.
    - [ ] Create components: Hero Section, Sparkline Chart (Recharts), and advanced Inputs.

## Phase 2: Data Reliability & Speed
**Objective:** Replace scraping with robust APIs and implement caching.

- [ ] **Data Providers**
    - [ ] Integration with a professional API (e.g., FMP or Alpha Vantage).
    - [ ] Implement `yfinance` as a fallback mechanism.
- [ ] **Caching Strategy (Redis)**
    - [ ] Set up Redis instance (local for dev, hosted for prod).
    - [ ] Implement caching decorator (30-60s TTL) for market data endpoints.
- [ ] **News Aggregation**
    - [ ] Upgrade news engine to use Gemini Grounding or a dedicated News API.

## Phase 3: "Agentic" AI Implementation
**Objective:** Move from single-shot analysis to reasoning agents.

- [ ] **Data Modeling**
    - [ ] Define Pydantic models for Structured Output (Verdict, Confidence, Reasoning).
- [ ] **Prompt Engineering**
    - [ ] Implement "Chain of Thought" prompting (XML tagging).
    - [ ] Create tools for Gemini (e.g., `calculate_rsi`, `get_volatility`).
- [ ] **User Context**
    - [ ] Add "Risk Profile" selector (Conservative, Moderate, Aggressive) to analysis request.

## Phase 4: DevOps & Cloud Infrastructure
**Objective:** Prepare for deployment on Google Cloud Platform.

- [ ] **Containerization**
    - [ ] Create `Dockerfile` for Backend (FastAPI).
    - [ ] Create `Dockerfile` for Frontend (Next.js).
- [ ] **Infrastructure**
    - [ ] Set up Google Cloud Project.
    - [ ] Configure Cloud Run services.
    - [ ] Set up Cloud SQL (PostgreSQL) instance.
- [ ] **CI/CD**
    - [ ] Update GitHub Actions to build and push Docker images to Artifact Registry.

## Phase 5: Feature Enhancements
- [ ] **Calculator Upgrade**
    - [ ] Add "Spread/Premium" field to calculator logic.
- [ ] **Technical Analysis**
    - [ ] Integrate `pandas-ta` for server-side indicator calculation (RSI, SMA, MACD).
- [ ] **User Auth**
    - [ ] Integrate Firebase Authentication or Supabase.

---
**Next Steps:**
- Await approval to begin Phase 1 (Backend Initialization).
