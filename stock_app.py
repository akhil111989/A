
import streamlit as st
import yfinance as yf

st.title("Simple Stock Screener")

stock = st.text_input("Enter Stock (e.g. TCS.NS or AAPL)")

if stock:
    data = yf.Ticker(stock)

    info = data.info

    st.subheader("Basic Info")
    st.write("Price:", info.get("currentPrice"))
    st.write("Market Cap:", info.get("marketCap"))
    st.write("52W High:", info.get("fiftyTwoWeekHigh"))
    st.write("52W Low:", info.get("fiftyTwoWeekLow"))

    st.subheader("Fundamentals")
    st.write("ROE:", info.get("returnOnEquity"))
    st.write("Debt:", info.get("totalDebt"))

    try:
        cf = data.cashflow
        fcf = cf.loc["Free Cash Flow"][0]
        st.write("Free Cash Flow:", fcf)
    except:
        st.write("Free Cash Flow: Not available")
