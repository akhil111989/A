import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Stable Stock Screener", layout="wide")

st.title("📊 Stable Multi-Source Stock Screener (NO yfinance)")

ticker = st.text_input("Enter NSE Ticker (RELIANCE, TCS, INFY)", "RELIANCE")


# ---------------- PRICE DATA (STOOQ - NO RATE LIMIT) ---------------- #
def get_price_data(symbol):
    try:
        url = f"https://stooq.com/q/d/l/?s={symbol.lower()}.ns&i=d"
        df = pd.read_csv(url)

        if df.empty:
            return None, None

        df["Date"] = pd.to_datetime(df["Date"])

        current = df["Close"].iloc[-1]
        ath = df["High"].max()
        atl = df["Low"].min()

        ath_date = df.loc[df["High"].idxmax(), "Date"].date()
        atl_date = df.loc[df["Low"].idxmin(), "Date"].date()

        correction = round((ath - current) / ath * 100, 2)

        return {
            "current": current,
            "ath": ath,
            "atl": atl,
            "ath_date": ath_date,
            "atl_date": atl_date,
            "correction": correction
        }, df

    except:
        return None, None


# ---------------- FUNDAMENTALS (SCREENER.IN) ---------------- #
def get_fundamentals(symbol):
    try:
        url = f"https://www.screener.in/company/{symbol}/"
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


# ---------------- EVENTS (PLACEHOLDER SAFE) ---------------- #
def get_events():
    return {
        "result_date": "Check NSE/BSE announcements",
        "dividend_date": "Check corporate actions"
    }


# ---------------- MAIN ---------------- #
if ticker:

    if st.button("Analyze"):

        price, df = get_price_data(ticker)
        fund = get_fundamentals(ticker)
        events = get_events()

        if price is None:
            st.error("No data found for this stock")
        else:

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

            st.divider()

            st.subheader("📅 Events")
            st.write("Result Date:", events["result_date"])
            st.write("Dividend Date:", events["dividend_date"])

            st.subheader("📉 Price Chart")
            st.line_chart(df["Close"])
