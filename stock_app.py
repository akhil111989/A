import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Advanced Stock Screener", layout="wide")

st.title("📊 Advanced Stock Screener (ATH / ATL / Fundamentals)")

ticker_input = st.text_input("Enter Stock Ticker (e.g. RELIANCE.NS, TCS.NS, AAPL)", "RELIANCE.NS")


# ---------------- HELPERS ---------------- #

def to_crores(value):
    try:
        return round(value / 1e7, 2)
    except:
        return None


def get_5y_avg_pe(history):
    try:
        pe_series = history["Close"] / history["Earnings"]
        return round(np.nanmean(pe_series), 2)
    except:
        return None


def get_stock_data(ticker):
    stock = yf.Ticker(ticker)

    info = stock.info
    hist = stock.history(period="5y")

    if hist.empty:
        return None, None

    # ATH / ATL
    ath = hist["High"].max()
    atl = hist["Low"].min()

    ath_date = hist["High"].idxmax().date()
    atl_date = hist["Low"].idxmin().date()

    current_price = hist["Close"].iloc[-1]

    # correction from ATH
    correction = round((ath - current_price) / ath * 100, 2)

    # Market cap
    market_cap = to_crores(info.get("marketCap", None))

    # PE
    pe = info.get("trailingPE", None)

    # Dividend yield
    div_yield = info.get("dividendYield", None)
    if div_yield:
        div_yield *= 100

    # ROCE approximation (ROE fallback if ROCE missing)
    roce = info.get("returnOnEquity", None)
    if roce:
        roce *= 100

    # Dividend date
    div_date = info.get("exDividendDate", None)

    # Free Cash Flow
    try:
        fcf = stock.cashflow.loc["Free Cash Flow"].iloc[0]
        fcf_crore = to_crores(fcf)
    except:
        fcf_crore = None

    # Earnings date (result date)
    earnings_date = info.get("earningsDate", None)

    return {
        "current_price": current_price,
        "ath": ath,
        "ath_date": ath_date,
        "atl": atl,
        "atl_date": atl_date,
        "correction_pct": correction,
        "market_cap_crore": market_cap,
        "pe": pe,
        "roce": roce,
        "dividend_yield": div_yield,
        "fcf_crore": fcf_crore,
        "earnings_date": earnings_date,
        "dividend_date": div_date
    }, hist


# ---------------- UI ---------------- #

if st.button("Analyze Stock"):

    data, hist = get_stock_data(ticker_input)

    if data is None:
        st.error("No data found. Check ticker.")
    else:

        col1, col2, col3 = st.columns(3)

        col1.metric("Current Price", round(data["current_price"], 2))
        col2.metric("ATH", f'{data["ath"]:.2f}', f'Date: {data["ath_date"]}')
        col3.metric("ATL", f'{data["atl"]:.2f}', f'Date: {data["atl_date"]}')

        st.divider()

        col4, col5, col6 = st.columns(3)

        col4.metric("Correction from ATH", f'{data["correction_pct"]}%')
        col5.metric("Market Cap (Cr)", data["market_cap_crore"])
        col6.metric("PE Ratio", data["pe"])

        col7, col8, col9 = st.columns(3)

        col7.metric("ROCE / ROE %", data["roce"])
        col8.metric("Dividend Yield %", data["dividend_yield"])
        col9.metric("FCF (Cr)", data["fcf_crore"])

        st.divider()

        st.subheader("📅 Key Events")

        st.write("**Earnings / Result Date:**", data["earnings_date"])
        st.write("**Dividend Date:**", data["dividend_date"])

        st.subheader("📉 Price Chart (5Y)")
        st.line_chart(hist["Close"])
