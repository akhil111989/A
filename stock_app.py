import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Stock Screener", layout="wide")

st.title("📊 Stock Screener (Stable Version)")

ticker = st.text_input("Enter ticker (e.g. RELIANCE.NS)", "RELIANCE.NS")

st.info("If data fails, it's due to Yahoo rate limits. Try again after a few seconds.")


def safe_fetch(ticker):

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5y")

        if hist is None or hist.empty:
            return None, None

        current = hist["Close"].iloc[-1]
        ath = hist["High"].max()
        atl = hist["Low"].min()

        ath_date = hist["High"].idxmax().date()
        atl_date = hist["Low"].idxmin().date()

        correction = round((ath - current) / ath * 100, 2)

        # SAFE fallback only (NO .info dependency)
        try:
            info = stock.fast_info
        except:
            info = {}

        return {
            "current": current,
            "ath": ath,
            "atl": atl,
            "ath_date": ath_date,
            "atl_date": atl_date,
            "correction": correction
        }, hist

    except:
        return None, None


if ticker:

    if st.button("Analyze"):

        data, hist = safe_fetch(ticker)

        if data is None:
            st.error("Data not available (Yahoo blocked or invalid ticker). Try again.")
        else:

            col1, col2, col3 = st.columns(3)

            col1.metric("Current", round(data["current"], 2))
            col2.metric("ATH", round(data["ath"], 2), str(data["ath_date"]))
            col3.metric("ATL", round(data["atl"], 2), str(data["atl_date"]))

            st.metric("Correction %", f'{data["correction"]}%')

            st.subheader("📉 Chart")
            st.line_chart(hist["Close"])

else:
    st.write("Enter a stock ticker and click Analyze.")
