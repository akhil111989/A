import streamlit as st
import yfinance as yf
import pandas as pd

st.title("Stock Screener Pro (Investor Edition)")

stock = st.text_input("Enter Stock (e.g. TCS.NS)")

def to_crore(x):
    try:
        return round(x / 1e7, 2)
    except:
        return "N/A"

if stock:
    try:
        ticker = yf.Ticker(stock)
        info = ticker.info
        hist = ticker.history(period="5y")

        price = info.get("currentPrice")
        market_cap = info.get("marketCap")

        ath = hist["Close"].max() if not hist.empty else None

        st.subheader("📊 Price & Valuation")

        st.write("Price:", price)
        st.write("Market Cap (₹ Cr):", to_crore(market_cap))
        st.write("ATH (5Y):", ath)

        if price and ath:
            correction = ((ath - price) / ath) * 100
            st.write("Correction from ATH (%):", round(correction, 2))

        # PE
        pe = info.get("trailingPE")
        st.write("Current PE:", pe)

        # Dividend Yield
        div_yield = info.get("dividendYield")
        if div_yield:
            st.write("Dividend Yield (%):", round(div_yield * 100, 2))
        else:
            st.write("Dividend Yield: N/A")

        st.subheader("📉 Fundamentals")

        roe = info.get("returnOnEquity")
        debt = info.get("totalDebt")

        st.write("ROE:", roe)
        st.write("Debt (₹ Cr):", to_crore(debt))

        # FCF
        try:
            cf = ticker.cashflow
            fcf = cf.loc["Free Cash Flow"][0]
            st.write("FCF (₹ Cr):", to_crore(fcf))

            # FCF Yield
            if market_cap and fcf:
                fcf_yield = (fcf / market_cap) * 100
                st.write("FCF Yield (%):", round(fcf_yield, 2))
        except:
            st.write("FCF / FCF Yield: Not available")

        # Approx 5Y Mean PE (proxy)
        try:
            earnings = info.get("trailingEps")
            if earnings and hist is not None:
                pe_series = hist["Close"] / earnings
                mean_pe = pe_series.mean()
                st.write("Approx 5Y Mean PE:", round(mean_pe, 2))
        except:
            st.write("5Y Mean PE: Not available")

    except:
        st.error("Error fetching data. Try correct stock symbol.")
