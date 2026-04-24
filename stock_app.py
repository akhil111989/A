import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(layout="wide")

st.title("⚓ STOCK DASHBOARD (STABLE VERSION)")

stocks_input = st.text_area(
    "Enter stocks (comma separated)",
    "RELIANCE.NS, TCS.NS, INFY.NS"
)

stocks = [s.strip() for s in stocks_input.split(",") if s.strip()]

# ---------- SAFE FETCH ----------
def get_stock(symbol):
    try:
        t = yf.Ticker(symbol)

        hist = t.history(period="1y")

        if hist is None or hist.empty:
            return {"Stock": symbol, "Error": "No price data"}

        price = float(hist["Close"].iloc[-1])
        ath = float(hist["Close"].max())
        atl = float(hist["Close"].min())

        ath_date = hist["Close"].idxmax()
        atl_date = hist["Close"].idxmin()

        # SAFE conversion
        try:
            ath_date = str(ath_date.date())
            atl_date = str(atl_date.date())
        except:
            ath_date = "NA"
            atl_date = "NA"

        correction = ((price - ath) / ath) * 100 if ath else 0

        # SAFE INFO (NO CRASH IF BLOCKED)
        try:
            info = t.get_info()
        except:
            info = {}

        pe = info.get("trailingPE", None)
        mcap = info.get("marketCap", None)

        if mcap:
            mcap = mcap / 1e7  # Cr

        # SIMPLE SCORE (NO COMPLEX LOGIC)
        score = 0
        if pe and pe < 25:
            score += 1
        if correction < -20:
            score += 1

        decision = "BUY" if score == 2 else "HOLD" if score == 1 else "WATCH"

        return {
            "Stock": symbol,
            "Price": round(price, 2),
            "ATH": round(ath, 2),
            "ATL": round(atl, 2),
            "ATH Date": ath_date,
            "ATL Date": atl_date,
            "Correction %": round(correction, 2),
            "PE": pe,
            "MCap (Cr)": mcap,
            "Score": score,
            "Decision": decision
        }

    except Exception as e:
        return {"Stock": symbol, "Error": str(e)}

# ---------- RUN ----------
if st.button("Run Analysis"):

    st.write("Processing stocks...")

    data = []

    for s in stocks:
        result = get_stock(s)
        data.append(result)

    df = pd.DataFrame(data)

    st.subheader("📊 Results")
    st.dataframe(df, use_container_width=True)

    # ---------- SUMMARY ----------
    if not df.empty:
        col1, col2, col3 = st.columns(3)

        col1.metric("Total Stocks", len(df))
        col2.metric("Buy Signals", len(df[df.get("Decision") == "BUY"]))
        col3.metric("Watch List", len(df[df.get("Decision") == "WATCH"]))
