import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

st.title("📊 Stock Screener - Institution Style")

# =========================
# INPUT
# =========================
stocks = st.text_input(
    "Enter Stock Symbols (comma separated, NSE format e.g. TCS.NS, INFY.NS):",
    "TCS.NS,INFY.NS,HDFCBANK.NS,RELIANCE.NS,ITC.NS"
)

stock_list = [s.strip() for s in stocks.split(",")]

# =========================
# FUNCTIONS
# =========================
def get_data(symbol):
    try:
        stock = yf.Ticker(symbol)

        info = stock.info
        hist = stock.history(period="5y")

        if hist.empty:
            return None

        current_price = hist["Close"].iloc[-1]
        ath_price = hist["Close"].max()

        market_cap = info.get("marketCap", np.nan)
        shares = info.get("sharesOutstanding", np.nan)

        # fallback if market cap missing
        if pd.isna(market_cap) and not pd.isna(shares):
            market_cap = current_price * shares

        ath_mcap = ath_price * shares if not pd.isna(shares) else np.nan

        correction = ((current_price - ath_price) / ath_price) * 100

        fcf = info.get("freeCashflow", np.nan)
        fcf_yield = (fcf / market_cap * 100) if market_cap and fcf else np.nan

        pe = info.get("trailingPE", np.nan)

        roe = info.get("returnOnEquity", np.nan)
        roce = roe * 100 if roe else np.nan  # proxy

        margins = info.get("profitMargins", np.nan)
        margins = margins * 100 if margins else np.nan

        growth = info.get("earningsGrowth", np.nan)
        growth = growth * 100 if growth else np.nan

        dividend = info.get("dividendYield", np.nan)
        dividend = dividend * 100 if dividend else np.nan

        # Dummy placeholders (Yahoo doesn't give properly)
        ath_pe = pe
        avg_pe = pe

        # Decision logic (basic)
        decision = "HOLD"
        if correction < -30 and fcf_yield and fcf_yield > 3:
            decision = "BUY"
        elif correction > -5:
            decision = "SELL"

        return {
            "Stock": symbol,
            "Market Cap (Cr)": market_cap / 1e7 if market_cap else np.nan,
            "Price": current_price,
            "ATH Price": ath_price,
            "ATH MCap (Cr)": ath_mcap / 1e7 if ath_mcap else np.nan,
            "Correction %": correction,
            "FCF (Cr)": fcf / 1e7 if fcf else np.nan,
            "FCF Yield %": fcf_yield,
            "PE": pe,
            "ATH PE": ath_pe,
            "5Y Avg PE": avg_pe,
            "ROCE %": roce,
            "Margins %": margins,
            "Profit Growth %": growth,
            "Dividend Yield %": dividend,
            "Decision": decision
        }

    except:
        return None

# =========================
# DATA FETCH
# =========================
data = []

with st.spinner("Fetching data..."):
    for s in stock_list:
        d = get_data(s)
        if d:
            data.append(d)

df = pd.DataFrame(data)

# =========================
# CLEAN + FORMAT
# =========================
if not df.empty:

    df.insert(0, "S.No", range(1, len(df) + 1))

    df = df.round(1)

    st.dataframe(df, use_container_width=True)

else:
    st.error("No data found. Check stock symbols.")
