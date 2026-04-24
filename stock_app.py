import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from bs4 import BeautifulSoup

st.set_page_config(layout="wide")
st.title("🚀 FULL INVESTING SYSTEM")

# ================= INPUT =================
stocks = st.text_input(
    "Enter Stocks (e.g. TCS, INFY, ITC):",
    "TCS,INFY,HDFCBANK,RELIANCE,ITC"
)

stock_list = [s.strip().upper() for s in stocks.split(",")]

# ================= SCREENER =================
def get_screener(symbol):
    try:
        url = f"https://www.screener.in/company/{symbol}/"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        ratios = {}
        for li in soup.select("li.flex.flex-space-between"):
            key = li.select_one("span.name").text.strip()
            val = li.select_one("span.number").text.strip()
            ratios[key] = val

        return {
            "PE": float(ratios.get("Stock P/E", "nan").replace(",", "")),
            "ROCE": float(ratios.get("ROCE", "nan").replace("%", "")),
            "Dividend": float(ratios.get("Dividend Yield", "0").replace("%", "")),
        }
    except:
        return {}

# ================= MAIN =================
def analyze(symbol):
    try:
        yf_symbol = symbol + ".NS"
        stock = yf.Ticker(yf_symbol)

        hist = stock.history(period="5y")
        info = stock.info
        cf = stock.cashflow
        fin = stock.financials

        if hist.empty:
            return None

        price = hist["Close"].iloc[-1]
        ath = hist["Close"].max()
        correction = ((price - ath) / ath) * 100

        shares = info.get("sharesOutstanding", np.nan)
        mcap = price * shares if shares else np.nan
        ath_mcap = ath * shares if shares else np.nan

        # FCF
        try:
            fcf = cf.loc["Total Cash From Operating Activities"][0] - cf.loc["Capital Expenditures"][0]
        except:
            fcf = np.nan

        fcf_yield = (fcf / mcap * 100) if mcap and fcf else np.nan

        # Screener data
        sc = get_screener(symbol)
        pe = sc.get("PE", np.nan)
        roce = sc.get("ROCE", np.nan)
        dividend = sc.get("Dividend", np.nan)

        # Growth
        growth = info.get("earningsGrowth", np.nan)
        growth = growth * 100 if growth else np.nan

        # Debt
        debt = info.get("totalDebt", np.nan)
        debt = debt / 1e7 if debt else np.nan

        # Score Engine
        score = 0
        if correction < -25: score += 2
        if fcf_yield and fcf_yield > 3: score += 2
        if roce and roce > 18: score += 2
        if growth and growth > 10: score += 1
        if debt and debt < (mcap/1e7)*0.5: score += 1

        if score >= 6:
            decision = "STRONG BUY"
        elif score >= 4:
            decision = "BUY"
        elif score >= 2:
            decision = "HOLD"
        else:
            decision = "SELL"

        return {
            "Stock": symbol,
            "Price": price,
            "MCap (Cr)": mcap/1e7 if mcap else np.nan,
            "ATH": ath,
            "Correction %": correction,
            "FCF Yield %": fcf_yield,
            "PE": pe,
            "ROCE %": roce,
            "Growth %": growth,
            "Dividend %": dividend,
            "Debt (Cr)": debt,
            "Score": score,
            "Decision": decision
        }

    except:
        return None

# ================= RUN =================
data = []

with st.spinner("Analyzing stocks..."):
    for s in stock_list:
        d = analyze(s)
        if d:
            data.append(d)

df = pd.DataFrame(data)

# ================= OUTPUT =================
if not df.empty:

    df = df.round(1)
    df = df.sort_values(by="Score", ascending=False)

    st.subheader("📊 Ranked Stocks")
    st.dataframe(df, use_container_width=True)

    # ================= PORTFOLIO =================
    st.subheader("💼 Portfolio Tracker")

    portfolio = st.text_input(
        "Enter your holdings (e.g. TCS:100, INFY:50)"
    )

    if portfolio:
        total = 0
        for item in portfolio.split(","):
            try:
                name, qty = item.split(":")
                qty = float(qty)

                price = df[df["Stock"] == name.strip()]["Price"].values[0]
                value = price * qty
                total += value

                st.write(f"{name} → ₹ {round(value,1)}")

            except:
                pass

        st.success(f"Total Portfolio Value: ₹ {round(total,1)}")

    # ================= WATCHLIST =================
    st.subheader("🚨 BUY Alerts")

    buys = df[df["Decision"].isin(["BUY","STRONG BUY"])]

    if not buys.empty:
        st.dataframe(buys, use_container_width=True)
    else:
        st.info("No BUY signals currently")

else:
    st.error("Check stock symbols")
