import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Multi-Source Stock Screener", layout="wide")

st.title("📊 Multi-Source Stock Intelligence Screener")

ticker = st.text_input("Enter Ticker (RELIANCE.NS, TCS.NS)", "RELIANCE.NS")

st.info("Uses Yahoo + Screener.in scraping + NSE fallback. Some data may be delayed.")


# ---------------- PRICE DATA (YAHOO) ---------------- #
def get_price_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5y")

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


# ---------------- SCREENER SCRAPING (INDIA FUNDAMENTALS) ---------------- #
def get_screener_data(symbol):
    try:
        url = f"https://www.screener.in/company/{symbol}/"
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        data = {}

        # PE, ROCE, etc appear in dt/dd blocks
        for row in soup.find_all("li"):
            text = row.text.strip()

            if "Stock P/E" in text:
                data["pe"] = text.split()[-1]

            if "ROCE" in text:
                data["roce"] = text.split()[-1]

            if "Dividend Yield" in text:
                data["dividend_yield"] = text.split()[-1]

        return data

    except:
        return {}


# ---------------- NSE RESULT / DIVIDEND PLACEHOLDER ---------------- #
def get_nse_events():
    # Placeholder structure (real NSE scraping can be added later)
    return {
        "result_date": "Check NSE/BSE announcements",
        "dividend_date": "Check corporate actions"
    }


# ---------------- RUN ---------------- #
if ticker:

    if st.button("Analyze"):

        price_data, hist = get_price_data(ticker)

        if price_data is None:
            st.error("No price data found")
        else:

            screener = get_screener_data(ticker.split(".")[0])
            events = get_nse_events()

            col1, col2, col3 = st.columns(3)

            col1.metric("Current Price", round(price_data["current"], 2))
            col2.metric("ATH", round(price_data["ath"], 2), str(price_data["ath_date"]))
            col3.metric("ATL", round(price_data["atl"], 2), str(price_data["atl_date"]))

            st.divider()

            col4, col5, col6 = st.columns(3)

            col4.metric("Correction %", f'{price_data["correction"]}%')
            col5.metric("PE", screener.get("pe", "NA"))
            col6.metric("ROCE", screener.get("roce", "NA"))

            col7, col8 = st.columns(2)

            col7.metric("Dividend Yield", screener.get("dividend_yield", "NA"))
            col8.metric("FCF", "Use Screener API / Pro version")

            st.divider()

            st.subheader("📅 Events")
            st.write("Result Date:", events["result_date"])
            st.write("Dividend Date:", events["dividend_date"])

            st.subheader("📉 Chart")
            st.line_chart(hist["Close"])
