import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import time
from datetime import datetime
from zoneinfo import ZoneInfo

# Load environment variables
load_dotenv()

# Import new modules
from src.data_provider import YahooProvider, MetalsApiProvider
from src.ai_engine import GoldAnalystEngine
from src.logger import log_prediction
from src.evaluator import Evaluator
from tools import fetch_gold_price, fetch_market_news, fetch_historical_data # Keep existing tools for specific grids
import plotly.graph_objects as go

# --- Page Config ---
st.set_page_config(
    page_title="Gold Analyst AI",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS (Apple Design System) ---
st.markdown("""
    <style>
    /* =======================================================
       1. DESIGN TOKENS (FIGMA / UI SYSTEM)
       ======================================================= */
    :root {
        /* COLOR TOKENS */
        /* Neutral Palette */
        --color-bg-primary: #FFFFFF;
        --color-bg-secondary: #F5F5F7;
        --color-surface: #FFFFFF;
        --color-surface-elevated: #F2F2F3;

        --color-text-primary: #0B0B0C;
        --color-text-secondary: #6E6E73;
        --color-text-tertiary: #A1A1A6;

        --color-divider: #D2D2D7;

        /* Accent Palette */
        --color-accent: #007AFF;
        --color-accent-hover: #2997FF;
        --color-accent-light: #E5F1FF;

        /* Status Colors */
        --color-buy: #12A851;   /* subtle green */
        --color-hold: #6E6E73;  /* neutral */
        --color-sell: #D93025;  /* apple-like muted red */

        /* TYPOGRAPHY TOKENS */
        --font-primary: "SF Pro", -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
        
        --font-size-hero: 64px;
        --font-size-title: 44px;
        --font-size-subtitle: 32px;
        --font-size-body-large: 20px;
        --font-size-body: 17px;
        --font-size-caption: 14px;

        /* SPACING TOKENS */
        --space-2xs: 4px;
        --space-xs: 8px;
        --space-sm: 12px;
        --space-md: 16px;
        --space-lg: 24px;
        --space-xl: 32px;
        --space-2xl: 48px;
        --space-3xl: 64px;

        /* RADIUS & SHADOW TOKENS */
        --radius-soft: 12px;
        --radius-medium: 16px;
        --radius-large: 24px;

        --shadow-subtle: 0px 2px 8px rgba(0,0,0,0.04);
        --shadow-card: 0px 8px 32px rgba(0,0,0,0.06);
    }

    /* =======================================================
       GLOBAL STYLES
       ======================================================= */
    .stApp {
        background-color: var(--color-bg-primary);
        font-family: var(--font-primary);
        color: var(--color-text-primary);
    }

    /* Layout: Centered, max-width 880px */
    .main .block-container {
        max-width: 880px;
        padding-top: var(--space-3xl);
        padding-bottom: var(--space-3xl);
        padding-left: var(--space-lg);
        padding-right: var(--space-lg);
    }

    /* Typography Defaults */
    h1 {
        font-size: var(--font-size-hero);
        font-weight: 600;
        letter-spacing: -0.02em;
        color: var(--color-text-primary);
        margin-bottom: var(--space-md);
    }
    
    h2 {
        font-size: var(--font-size-title);
        font-weight: 600;
        letter-spacing: -0.01em;
        color: var(--color-text-primary);
        margin-top: var(--space-3xl);
        margin-bottom: var(--space-xl);
    }

    h3 {
        font-size: var(--font-size-subtitle);
        font-weight: 500;
        color: var(--color-text-primary);
        margin-bottom: var(--space-lg);
    }

    p, div, span {
        font-size: var(--font-size-body);
        line-height: 1.5;
        color: var(--color-text-primary);
    }

    /* =======================================================
       COMPONENTS
       ======================================================= */
    
    /* Navbar (Minimal) */
    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 72px;
        padding: 0 var(--space-xl);
        margin-bottom: var(--space-2xl);
        border-bottom: 1px solid transparent; /* Optional */
    }
    
    /* Recommendation Card */
    .rec-card {
        background-color: var(--color-surface-elevated);
        border-radius: var(--radius-large);
        padding: var(--space-xl);
        text-align: center;
        box-shadow: var(--shadow-card);
        margin-bottom: var(--space-2xl);
        border: 2px solid transparent;
        transition: opacity 0.2s ease-out;
    }
    
    .rec-buy { border-color: var(--color-buy); }
    .rec-sell { border-color: var(--color-sell); }
    .rec-hold { border-color: var(--color-hold); }

    .rec-action {
        font-size: var(--font-size-title);
        font-weight: 700;
        margin: var(--space-sm) 0;
    }

    /* Metric Card */
    .metric-card {
        background-color: var(--color-surface);
        border-radius: var(--radius-medium);
        padding: var(--space-lg);
        box-shadow: var(--shadow-subtle);
        border: 1px solid var(--color-divider);
        height: 100%;
    }

    /* Inputs */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #1c1c1e !important; /* Dark background */
        color: white !important;
        border-radius: var(--radius-soft) !important;
        border: 1px solid var(--color-divider) !important;
        height: 48px !important;
    }
    
    /* Ensure text inside selectbox is white */
    .stSelectbox div[data-baseweb="select"] div {
        color: white !important;
    }
    
    /* Dropdown menu items */
    div[data-baseweb="popover"] div, div[data-baseweb="popover"] li {
        color: white !important;
        background-color: #1c1c1e !important;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #E5E5EA !important; /* Light Grey */
        color: #1D1D1F !important; /* Dark Grey */
        border-radius: var(--radius-soft) !important;
        padding: 14px 22px !important;
        font-size: 17px !important;
        font-weight: 500 !important;
        border: none !important;
        box-shadow: var(--shadow-subtle) !important;
        transition: background 150ms !important;
    }
    
    .stButton button:hover {
        background-color: #D1D1D6 !important; /* Darker Grey */
        transform: translateY(-2px);
    }

    /* Expander Header - Force Light Grey in all states */
    .streamlit-expanderHeader,
    div[data-testid="stExpander"] details summary,
    div[data-testid="stExpander"] details[open] summary {
        background-color: #F5F5F7 !important;
        color: #1D1D1F !important;
        border-radius: var(--radius-soft) !important;
        border: none !important;
    }
    
    .streamlit-expanderHeader:hover,
    div[data-testid="stExpander"] details summary:hover,
    div[data-testid="stExpander"] details[open] summary:hover {
        background-color: #E5E5EA !important;
        color: #1D1D1F !important;
    }

    .streamlit-expanderHeader p,
    div[data-testid="stExpander"] details summary p {
        color: #1D1D1F !important;
        font-weight: 600 !important;
    }
    
    /* Fix for the SVG icon color */
    .streamlit-expanderHeader svg,
    div[data-testid="stExpander"] details summary svg {
        fill: #1D1D1F !important;
        color: #1D1D1F !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- Navbar ---
now_utc = datetime.now(ZoneInfo("UTC"))
now_uae = datetime.now(ZoneInfo("Asia/Dubai"))
now_egypt = datetime.now(ZoneInfo("Africa/Cairo"))

time_str = f"{now_utc.strftime('%b %d, %Y')} • GMT {now_utc.strftime('%I:%M %p')} • UAE {now_uae.strftime('%I:%M %p')} • EGY {now_egypt.strftime('%I:%M %p')}"

st.markdown(f"""
<div class="navbar">
    <div style="font-size: 20px; font-weight: 700; letter-spacing: -0.02em;">GOLD ANALYST AI</div>
    <div style="font-size: 14px; color: var(--color-text-tertiary);">Updated: {time_str}</div>
</div>
""", unsafe_allow_html=True)

# --- Main Logic ---
if 'last_run' not in st.session_state:
    st.session_state['last_run'] = None
    st.session_state['ai_result'] = None

# Providers
yahoo = YahooProvider()
metals = MetalsApiProvider()
engine = GoldAnalystEngine()
evaluator = Evaluator()

# Fetch Data
with st.spinner("Fetching live market data..."):
    gld = yahoo.get_latest("GLD")
    xau = metals.get_latest("XAU")
    
    if gld and xau:
        # --- Hero Price Display ---
        # GLD Price: $192.23 | Change: +1.23%
        gld_price = gld['price']
        gld_change = gld['pct_change_24h']
        change_color = "var(--color-buy)" if gld_change >= 0 else "var(--color-sell)"
        change_sign = "+" if gld_change >= 0 else ""
        
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 48px;">
            <div style="font-size: 16px; font-weight: 600; color: var(--color-text-secondary); margin-bottom: 8px;">SPDR GOLD SHARES (GLD)</div>
            <div style="font-size: 64px; font-weight: 600; letter-spacing: -0.02em; color: var(--color-text-primary); line-height: 1;">
                ${gld_price:.2f}
            </div>
            <div style="font-size: 20px; font-weight: 500; color: {change_color}; margin-top: 8px;">
                {change_sign}{gld_change}%
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Run AI Analysis (Only if not run recently or forced)
        if st.button("Generate New Analysis") or st.session_state['ai_result'] is None:
            result = engine.analyze(gld, xau)
            st.session_state['ai_result'] = result
            st.session_state['last_run'] = time.time()
            
            # Log to DB
            if result and "output" in result:
                log_prediction(gld['price'], xau['price'], result['input'], result['output'])
                
            # Run Evaluation
            evaluator.run_evaluation()

# --- Recommendation Card ---
if st.session_state['ai_result']:
    res = st.session_state['ai_result']['output']
    action = res.get('final_action', 'HOLD')
    conf = res.get('confidence', 0)
    brief = res.get('rationale_brief', '')
    tech = res.get('rationale_technical', '')
    
    # Map action to color variable
    color_var = "var(--color-hold)"
    if action == "BUY": color_var = "var(--color-buy)"
    if action == "SELL": color_var = "var(--color-sell)"
    
    st.markdown(f"""
    <div class="rec-card" style="border-color: {color_var};">
        <div style="font-size: 44px; font-weight: 700; color: {color_var}; letter-spacing: -0.02em;">{action}</div>
        <div style="font-size: 17px; font-weight: 500; color: var(--color-text-secondary); margin-top: 8px;">Confidence: {conf}%</div>
        <div style="font-size: 20px; font-weight: 400; color: var(--color-text-primary); margin-top: 24px; line-height: 1.4;">{brief}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Metrics Grid ---
    metrics = evaluator.get_metrics()
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 14px; font-weight: 600; color: var(--color-text-tertiary);">Model Accuracy</div>
            <div style="font-size: 24px; font-weight: 500; margin-top: 8px;">{metrics['accuracy']}%</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 14px; font-weight: 600; color: var(--color-text-tertiary);">Spot Gold</div>
            <div style="font-size: 24px; font-weight: 500; margin-top: 8px;">${xau['price']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 14px; font-weight: 600; color: var(--color-text-tertiary);">Forecast Horizon</div>
            <div style="font-size: 24px; font-weight: 500; margin-top: 8px;">24 Hours</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 14px; font-weight: 600; color: var(--color-text-tertiary);">Risk Tier</div>
            <div style="font-size: 24px; font-weight: 500; margin-top: 8px;">{res.get('suggested_risk_tier', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)

    # --- Sparkline (Historical) ---
    st.markdown("<div style='margin-top: 48px;'></div>", unsafe_allow_html=True)
    hist_data = fetch_historical_data(period="1mo")
    if hist_data is not None and not hist_data.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist_data.index, 
            y=hist_data['Close'], 
            mode='lines', 
            line=dict(color='#0071E3', width=3),
            fill='tozeroy',
            fillcolor='rgba(0, 113, 227, 0.05)'
        ))
        fig.update_layout(
            height=200,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # --- Advanced Panel ---
    with st.expander("▸ Advanced Insights", expanded=False):
        st.markdown(f"""
        <div style="padding: 24px;">
            <div style="font-size: 17px; font-weight: 600; margin-bottom: 8px;">Technical Rationale</div>
            <div style="font-size: 17px; line-height: 1.5; color: var(--color-text-secondary); margin-bottom: 24px;">{tech}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # News inside Advanced
        st.markdown("<h3>Latest Market News</h3>", unsafe_allow_html=True)
        news_items = fetch_market_news()
        if isinstance(news_items, list) and news_items:
            for item in news_items[:3]: # Show top 3
                st.markdown(f"""
                <div style="padding: 16px; border-bottom: 1px solid var(--color-divider);">
                    <div style="font-size: 12px; font-weight: 600; color: var(--color-text-tertiary); text-transform: uppercase;">{item.get('source', 'News')}</div>
                    <a href="{item.get('link')}" target="_blank" style="text-decoration: none; color: var(--color-text-primary); font-weight: 500; font-size: 16px;">{item.get('title')}</a>
                </div>
                """, unsafe_allow_html=True)

# --- Regional Markets & Calculator ---
st.markdown("<h2>Regional Markets & Calculator</h2>", unsafe_allow_html=True)

# Fetch detailed regional data using the existing tool
detailed_data = fetch_gold_price()

if detailed_data and "usd" in detailed_data:
    rates = detailed_data.get('rates', {})
    usd_prices = detailed_data.get('usd', {})
    egp_prices = detailed_data.get('egypt', {})
    uae_prices = detailed_data.get('uae', {})

    m1, m2, m3 = st.columns(3)
    
    def price_card_content(title, prices, currency):
        rows_html = ""
        for k, v in prices.items():
            rows_html += f"""<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid var(--color-divider); padding-bottom: 8px;">
<span style="font-weight: 500; color: var(--color-text-secondary); font-size: 15px;">{k}</span>
<span style="font-weight: 600; font-size: 18px; color: var(--color-text-primary); font-family: var(--font-primary);">{v:,.2f} <span style="font-size: 12px; color: var(--color-text-tertiary);">{currency}</span></span>
</div>"""
        return f"""<div class="metric-card"><div class="card-header">{title}</div>{rows_html}</div>"""

    with m1:
        st.markdown(price_card_content("🌍 International (USD)", usd_prices, "USD"), unsafe_allow_html=True)
    with m2:
        st.markdown(price_card_content("🇪🇬 Egypt (EGP)", egp_prices, "EGP"), unsafe_allow_html=True)
    with m3:
        st.markdown(price_card_content("🇦🇪 UAE (AED)", uae_prices, "AED"), unsafe_allow_html=True)

    # Calculator
    with st.container():
        st.markdown("<div class='metric-card' style='margin-top: 24px;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0;'>Gold Value Calculator</h3>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
        
        with c1:
            weight = st.number_input("Weight (grams)", min_value=0.1, value=5.0, step=0.1)
        with c2:
            karat = st.selectbox("Karat", ["24k", "21k", "18k"])
        with c3:
            market = st.selectbox("Market", ["International (USD)", "Egypt (EGP)", "UAE (AED)"])
        
        price_per_gram = 0
        currency = "USD"
        
        if "International" in market:
            price_per_gram = usd_prices.get(karat, 0)
            currency = "USD"
        elif "Egypt" in market:
            price_per_gram = egp_prices.get(karat, 0)
            currency = "EGP"
        elif "UAE" in market:
            price_per_gram = uae_prices.get(karat, 0)
            currency = "AED"
            
        total_value = weight * price_per_gram
        
        with c4:
            st.markdown(f"""
            <div style="text-align: right;">
                <div style="font-size: 12px; color: var(--color-text-tertiary); text-transform: uppercase; margin-bottom: 4px;">Estimated Value</div>
                <div style="font-size: 32px; font-weight: 600; color: var(--color-text-primary);">{total_value:,.2f} {currency}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- Footer ---
st.markdown("<div style='text-align: center; margin-top: 64px; color: var(--color-text-tertiary); font-size: 14px;'>Informational only — not financial advice.</div>", unsafe_allow_html=True)
