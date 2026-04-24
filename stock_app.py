import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time

st.set_page_config(layout="wide")

stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ITC.NS"]

# =========================
# SAFE DATA FETCH (NO INFO API)
# =========================
def get_stock(symbol):
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period="5y")

        if hist is None or hist.empty:
            return None

        close = hist["Close"]

        price = close.iloc[-1]
        ath = close.max()
        atl = close.min()

        ath_date = close.idxmax().date()
        atl_date = close.idxmin().date()

        correction = ((price - ath) / ath) * 100

        returns = close.pct_change().dropna()
        volatility = returns.std()

        # =========================
        # ELITE SCORE MODEL
        # =========================
        score = 0

        # Deep correction opportunity
        if correction < -40:
            score += 3
        elif correction < -25:
            score += 2
        elif correction < -15:
            score += 1

        # Stability
        if volatility < 0.02:
            score += 1

        # Trend filter
        sma_50 = close.rolling(50).mean().iloc[-1]
        if price > sma_50:
            score += 1

        # BUY / SELL logic
        if score >= 4:
            signal = "BUY"
        elif score <= 1:
            signal = "AVOID"
        else:
            signal = "WATCH"

        return {
            "Stock": symbol,
            "Price": round(price, 2),
            "ATH": round(ath, 2),
            "ATL": round(atl, 2),
            "ATH Date": ath_date,
            "ATL Date": atl_date,
            "Correction %": round(correction, 2),
            "Volatility": round(volatility, 5),
            "Score": score,
            "Signal": signal
        }

    except Exception as e:
        return {
            "Stock": symbol,
            "Price": None,
            "ATH": None,
            "ATL": None,
            "ATH Date": None,
            "ATL Date": None,
            "Correction %": None,
            "Volatility": None,
            "Score": 0,
            "Signal": "ERROR"
        }

# =========================
# UI
# =========================
st.title("📊 Elite Stock Intelligence Model")

data = []

progress = st.progress(0)

for i, s in enumerate(stocks):
    data.append(get_stock(s))
    progress.progress((i + 1) / len(stocks))
    time.sleep(0.5)  # prevents rate limit

df = pd.DataFrame(data)

st.dataframe(df, use_container_width=True)

st.markdown("### 🧠 Signals Summary")

col1, col2, col3 = st.columns(3)

col1.metric("BUY", len(df[df["Signal"] == "BUY"]))
col2.metric("WATCH", len(df[df["Signal"] == "WATCH"]))
col3.metric("AVOID", len(df[df["Signal"] == "AVOID"]))
