import streamlit as st
import yfinance as yf
import pandas as pd
import time

# =========================
# STOCK LIST
# =========================
stocks = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ITC.NS"
]

# =========================
# SAFE FETCH (NO CRASH)
# =========================
@st.cache_data(ttl=3600)
def get_stock(symbol):

    t = yf.Ticker(symbol)
    hist = t.history(period="5y").dropna()

    price = hist["Close"].iloc[-1]

    ath = hist["Close"].max()
    atl = hist["Close"].min()

    ath_date = hist["Close"].idxmax().strftime("%d-%b-%Y")
    atl_date = hist["Close"].idxmin().strftime("%d-%b-%Y")

    correction = (price - ath) / ath * 100

    # SAFE DATA ONLY
    fi = {}
    try:
        fi = t.fast_info
    except:
        pass

    pe = fi.get("trailing_pe", None)
    market_cap = fi.get("market_cap", None)

    # =========================
    # SIMPLE QUALITY MODEL (YOUR ORIGINAL STYLE)
    # =========================
    score = 0

    # Quality
    if pe and pe < 25:
        score += 1

    # Opportunity
    if correction < -20:
        score += 1

    # Stability (volatility proxy)
    returns = hist["Close"].pct_change().dropna()
    volatility = returns.std()

    if volatility < 0.02:
        score += 1

    # Debt proxy (not always available → safe handling)
    debt = None
    try:
        debt = fi.get("debt_to_equity", None)
    except:
        pass

    if debt is not None and debt < 1:
        score
