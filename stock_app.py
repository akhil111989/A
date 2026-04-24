import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
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
# CACHE (IMPORTANT FOR STREAMLIT)
# =========================
@st.cache_data(ttl=3600)
def get_stock(symbol):

    t = yf.Ticker(symbol)

    # =========================
    # PRICE DATA
    # =========================
    hist = t.history(period="max").dropna()

    price = hist["Close"].iloc[-1]

    ath = hist["Close"].max()
    atl = hist["Close"].min()

    ath_date = hist["Close"].idxmax().strftime("%d-%b-%Y")
    atl_date = hist["Close"].idxmin().strftime("%d-%b-%Y")

    correction = (price - ath) / ath * 100

    # =========================
    # SAFE FUNDAMENTALS (NO .info = NO RATE LIMIT CRASH)
    # =========================
    try:
        fi = t.fast_info
    except:
        fi = {}

    pe = fi.get("trailing_pe", None)
    debt = fi.get("debt_to_equity", None)

    # =========================
    # OPTIONAL CALENDAR (SAFE TRY)
    # =========================
    try:
        cal = t.calendar
        result_date = str(cal.loc["Earnings Date"][0].date())
    except:
        result_date = "NA"

    try:
        ex_div = str(cal.loc["Ex-Dividend Date"][0].date())
    except:
        ex_div = "NA"

    # =========================
    # ELITE SCORE (CLEAN VERSION)
    # =========================
    score = 0

    # VALUE
    if pe and pe < 25:
        score += 1

    # MOMENTUM (deep correction = opportunity)
    if correction < -20:
        score += 1

    # RISK
    if debt is not None and debt < 1:
        score += 1

    # (Growth / ROE skipped safely because unreliable in fast_info)

    # =========================
    # FINAL DECISION
    # =========================
    if score >= 3:
        decision = "STRONG BUY"
    elif score == 2:
        decision = "BUY"
    elif score == 1:
        decision = "HOLD"
    else:
        decision = "SELL"

    return {
        "Stock": symbol,
        "Price": price,
        "PE": pe,
        "Debt": debt,
        "ATH": ath,
        "ATL": atl,
        "ATH Date": ath_date,
        "ATL Date": atl_date,
        "Correction %": correction,
        "Result Date": result_date,
        "Ex-Dividend": ex_div,
        "Score": score,
        "Decision": decision
    }


# =========================
# RUN ENGINE (RATE LIMIT SAFE)
# =========================
data = []

for s in stocks:
    data.append(get_stock(s))
    time.sleep(1.5)   # IMPORTANT: prevents Yahoo block

df = pd.DataFrame(data)

# =========================
# DISPLAY DASHBOARD
# =========================
st.title("⚓ Elite Stock Screener Dashboard")

st.dataframe(df)

# =========================
# SUMMARY PANEL
# =========================
st.subheader("📊 Summary")

st.write("Total Stocks:", len(df))
st.write("Strong Buy:", len(df[df["Decision"] == "STRONG BUY"]))
st.write("Buy:", len(df[df["Decision"] == "BUY"]))
st.write("Sell:", len(df[df["Decision"] == "SELL"]))
