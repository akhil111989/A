import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Indian Stock Intelligence Screener", layout="wide")


# -----------------------------
# CACHE (prevents repeated API calls)
# -----------------------------
@st.cache_data(ttl=3600)
def load_stock(ticker):

    stock = yf.Ticker(ticker)
    hist = stock.history(period="max")

    if hist.empty:
        return None

    info = stock.info

    # -----------------------------
    # PRICE METRICS
    # -----------------------------
    current_price = hist["Close"].iloc[-1]

    ath = hist["Close"].max()
    atl = hist["Close"].min()

    ath_date = hist["Close"].idxmax().date()
    atl_date = hist["Close"].idxmin().date()

    correction_from_ath = ((ath - current_price) / ath) * 100

    # -----------------------------
    # MARKET CAP
    # -----------------------------
    market_cap = info.get("marketCap", np.nan)
    market_cap_cr = market_cap / 1e7 if market_cap else np.nan

    # -----------------------------
    # PE & ROE
    # -----------------------------
    pe = info.get("trailingPE", np.nan)
    roe = info.get("returnOnEquity", np.nan)
    roe = roe * 100 if roe else np.nan

    # -----------------------------
    # DIVIDEND
    # -----------------------------
    div_yield = info.get("dividendYield", 0)
    div_yield = div_yield * 100 if div_yield else 0

    # -----------------------------
    # FREE CASH FLOW
    # -----------------------------
    try:
        cashflow = stock.cashflow
        ocf = cashflow.loc["Total Cash From Operating Activities"].iloc[0]
        capex = cashflow.loc["Capital Expenditures"].iloc[0]
        fcf = ocf - capex
    except:
        fcf = np.nan

    fcf_yield = (fcf / market_cap) * 100 if market_cap and fcf else np.nan

    # -----------------------------
    # EARNINGS DATE
    # -----------------------------
    try:
        earnings = stock.calendar
        earnings_date = earnings.iloc[0, 0]
    except:
        earnings_date = "N/A"

    # -----------------------------
    # DIVIDEND DATE
    # -----------------------------
    try:
        div_date = stock.dividends
        last_div_date = div_date.index[-1].date()
    except:
        last_div_date = "N/A"

    return {
        "ticker": ticker,
        "price": current_price,
        "market_cap_cr": market_cap_cr,
        "ath": ath,
        "ath_date": ath_date,
        "atl": atl,
        "atl_date": atl_date,
        "correction_pct": correction_from_ath,
        "pe": pe,
        "roe": roe,
        "div_yield": div_yield,
        "fcf": fcf,
        "fcf_yield": fcf_yield,
        "earnings_date": earnings_date,
        "dividend_date": last_div_date
    }


# -----------------------------
# UI
# -----------------------------
st.title("📊 Indian Stock Intelligence Screener (Multi-Source Fusion)")

ticker_input = st.text_input("Enter NSE Stock (e.g. RELIANCE.NS, TCS.NS, INFY.NS)")

if ticker_input:

    data = load_stock(ticker_input)

    if data is None:
        st.error("No data found. Check ticker format like RELIANCE.NS")
        st.stop()

    # -----------------------------
    # TOP METRICS
    # -----------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Price", round(data["price"], 2))
    col2.metric("Market Cap (Cr)", round(data["market_cap_cr"], 2))
    col3.metric("PE", round(data["pe"], 2) if data["pe"] else "N/A")
    col4.metric("ROE %", round(data["roe"], 2) if data["roe"] else "N/A")

    st.divider()

    # -----------------------------
    # CORE VALUE METRICS
    # -----------------------------
    st.subheader("📌 Valuation & Performance")

    df = pd.DataFrame([{
        "ATH": data["ath"],
        "ATH Date": data["ath_date"],
        "ATL": data["atl"],
        "ATL Date": data["atl_date"],
        "Correction % from ATH": round(data["correction_pct"], 2),
        "Dividend Yield %": round(data["div_yield"], 2),
        "FCF": data["fcf"],
        "FCF Yield %": round(data["fcf_yield"], 2) if data["fcf_yield"] else None
    }])

    st.dataframe(df, use_container_width=True)

    # -----------------------------
    # EVENTS
    # -----------------------------
    st.subheader("📅 Upcoming & Recent Events")

    st.write(f"📊 Earnings Date: {data['earnings_date']}")
    st.write(f"💰 Last Dividend Date: {data['dividend_date']}")
