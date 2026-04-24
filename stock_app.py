import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Smart Stock Screener", layout="wide")

st.title("📊 Smart Multi-Market Stock Screener")

ticker = st.text_input("Enter ticker (RELIANCE.NS / TCS.NS / AAPL)", "RELIANCE.NS")


# ---------------- DETECT MARKET ---------------- #
def is_indian(ticker):
    return ".NS" in ticker or ".BO" in ticker


# ---------------- INDIA PRICE (NSE via Yahoo fallback removed issue) ---------------- #
def get_india_price(symbol):
    try:
        # Screener fallback proxy (reliable scraping source)
        url = f"https://www.screener.in/company/{symbol.split('.')[0]}/"
        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            return None, None

        soup = BeautifulSoup(r.text, "html.parser")

        prices = {}

        # Extract from page tables (light parsing)
        for td in soup.find_all("td"):
            text = td.text.strip()

        # fallback: use yfinance ONLY for price (safer than full data)
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1y")

        if hist.empty:
            return None, None

        current = hist["Close"].iloc[-1]
        ath = hist["High"].max()
        atl = hist["Low"].min()

        ath_date = hist["High"].idxmax().date()
        atl_date = hist["Low"].idxmin().date()

        correction = round((ath - current) / ath * 100, 2)

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


# ---------------- US PRICE ---------------- #
def get_us_price(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="5y")

    if hist.empty:
        return None, None

    current = hist["Close"].iloc[-1]
    ath = hist["High"].max()
    atl = hist["Low"].min()

    return {
        "current": current,
        "ath": ath,
        "atl": atl,
        "ath_date": hist["High"].idxmax().date(),
        "atl_date": hist["Low"].idxmin().date(),
        "correction": round((ath - current) / ath * 100, 2)
    }, hist


# ---------------- FUNDAMENTALS (SCRAPER SAFE) ---------------- #
def get_fundamentals(symbol):
    try:
        url = f"https://www.screener.in/company/{symbol.split('.')[0]}/"
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        data = {}

        for li in soup.find_all("li"):
            text = li.text.strip()

            if "Stock P/E" in text:
                data["pe"] = text.split()[-1]

            if "ROCE" in text:
                data["roce"] = text.split()[-1]

            if "Dividend Yield" in text:
                data["dividend_yield"] = text.split()[-1]

        return data

    except:
        return {}


# ---------------- MAIN ---------------- #
if ticker:

    if st.button("Analyze"):

        if is_indian(ticker):
            price, hist = get_india_price(ticker)
        else:
            price, hist = get_us_price(ticker)

        if price is None:
            st.error("❌ No data found. Try another ticker or check format.")
        else:

            fund = get_fundamentals(ticker)

            col1, col2, col3 = st.columns(3)

            col1.metric("Current", round(price["current"], 2))
            col2.metric("ATH", round(price["ath"], 2), str(price["ath_date"]))
            col3.metric("ATL", round(price["atl"], 2), str(price["atl_date"]))

            st.divider()

            col4, col5, col6 = st.columns(3)

            col4.metric("Correction %", f'{price["correction"]}%')
            col5.metric("PE", fund.get("pe", "NA"))
            col6.metric("ROCE", fund.get("roce", "NA"))

            col7 = st.columns(1)[0]
            col7.metric("Dividend Yield", fund.get("dividend_yield", "NA"))

            st.subheader("📉 Price Chart")
            st.line_chart(hist["Close"])
