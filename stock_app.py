import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from bs4 import BeautifulSoup

st.set_page_config(layout="wide")
st.title("🚀 Multi-Source Stock Engine")

# ================= INPUT =================
stocks = st.text_input(
    "Enter NSE Stocks (e.g. TCS, INFY, ITC):",
    "TCS,INFY,HDFCBANK,RELIANCE,ITC"
)

stock_list = [s.strip().upper() for s in stocks.split(",")]

# ================= SAFE =================
def safe(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "-"
    return round(x, 1)

# ================= SCREENER =================
def get_screener(symbol):
    try:
        url = f"https://www.screener.in/company/{symbol}/"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        ratios = {}
        for li in soup.select("li.flex.flex-space-between"):
            key = li.select_one("span.name").text.strip()
            val = li.select_one("span.number").text.strip()
            ratios[key] = val

        def clean(x):
            return float(x.replace(",", "").replace("%", "")) if x else np.nan

        return {
            "PE": clean(ratios.get("Stock P/E")),
            "ROCE": clean(ratios.get("ROCE")),
            "Dividend": clean(ratios.get("Dividend Yield")),
            "MCap": clean(ratios.get("Market Cap"))
        }
    except:
        return {}

# ================= MONEYCONTROL (LIMITED) =================
def get_moneycontrol(symbol):
    try:
        url = f"https://www.moneycontrol.com/india/stockpricequote/{symbol}"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)

        # very limited fallback (not reliable always)
        if "price" in r.text.lower():
            return {"ok": True}
        return {}
    except:
        return {}

# ================= MAIN =================
def analyze(symbol):
    try:
        yf_symbol = symbol + ".NS"
        stock = yf.Ticker(yf_symbol)

        hist = stock.history(period="5y")

        if hist.empty:
            return None

        # ===== PRICE =====
        price = hist["Close"].dropna().iloc[-1]
        ath = hist["Close"].max()
        correction = ((price - ath) / ath) * 100

        # ===== SOURCES =====
        sc = get_screener(symbol)
        mc = get_moneycontrol(symbol)

        # ===== MARKET CAP =====
        mcap = sc.get("MCap", np.nan)

        # fallback to yfinance if needed
        if pd.isna(mcap):
            try:
                info = stock.info
                shares = info.get("sharesOutstanding")
                if shares:
                    mcap = (shares * price) / 1e7
            except:
                pass

        # ===== SHARES =====
        shares = (mcap * 1e7) / price if mcap else np.nan

        # ===== ATH MCAP =====
        ath_mcap = (ath * shares) / 1e7 if shares else np.nan

        # ===== FCF =====
        try:
            cf = stock.cashflow
            fcf = cf.loc["Total Cash From Operating Activities"][0] - cf.loc["Capital Expenditures"][0]
            fcf_cr = fcf / 1e7
        except:
            fcf_cr = np.nan

        fcf_yield = (fcf_cr / mcap * 100) if mcap and fcf_cr else np.nan

        # ===== FUNDAMENTALS =====
        pe = sc.get("PE", np.nan)
        roce = sc.get("ROCE", np.nan)
        dividend = sc.get("Dividend", np.nan)

        # ===== GROWTH =====
        try:
            info = stock.info
            growth = info.get("earningsGrowth", np.nan)
            growth = growth * 100 if growth else np.nan
        except:
            growth = np.nan

        # ===== SCORE =====
        score = 0
        if correction < -25: score += 2
        if fcf_yield and fcf_yield > 3: score += 2
        if roce and roce > 18: score += 2
        if growth and growth > 10: score += 1

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
            "MCap (Cr)": mcap,
            "ATH Price": ath,
            "ATH MCap (Cr)": ath_mcap,
            "Correction %": correction,
            "FCF (Cr)": fcf_cr,
            "FCF Yield %": fcf_yield,
            "PE": pe,
            "ROCE %": roce,
            "Growth %": growth,
            "Dividend %": dividend,
            "Score": score,
            "Decision": decision
        }

    except:
        return None

# ================= RUN =================
data = []

with st.spinner("Fetching from multiple sources..."):
    for s in stock_list:
        d = analyze(s)
        if d:
            data.append(d)

df = pd.DataFrame(data)

if not df.empty:
    df.insert(0, "S.No", range(1, len(df) + 1))

    for col in df.columns:
        if col not in ["Stock", "Decision"]:
            df[col] = df[col].apply(safe)

    st.dataframe(df, use_container_width=True)

else:
    st.error("Check stock symbols")
