import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# =========================
# CONFIG
# =========================

STOCKS = [
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK",
    "LT",
    "TATAMOTORS",
    "ITC"
]

# =========================
# DATA LAYER
# =========================

class DataProvider:

    def get_fundamentals(self, symbol):

        try:
            t = yf.Ticker(symbol + ".NS")
            info = t.info

            return {
                "pe": info.get("trailingPE"),
                "pb": info.get("priceToBook"),
                "roe": info.get("returnOnEquity"),
                "debt_to_equity": info.get("debtToEquity"),
                "profit_margin": info.get("profitMargins"),
                "revenue_growth": info.get("revenueGrowth"),
                "dividend_yield": info.get("dividendYield")
            }

        except:
            return {}

    def get_price(self, symbol):

        try:
            df = yf.download(symbol + ".NS", period="2y", progress=False)
            df.dropna(inplace=True)
            return df
        except:
            return pd.DataFrame()


# =========================
# FEATURE ENGINEERING
# =========================

def safe(val, default=0):
    if val is None or pd.isna(val):
        return default
    return val


def compute_technical(df):

    if df.empty:
        return {
            "momentum_1y": 0,
            "volatility": 0,
            "drawdown": 0
        }

    df["ret"] = df["Close"].pct_change()

    momentum_1y = (df["Close"].iloc[-1] / df["Close"].iloc[0] - 1)
    volatility = df["ret"].std() * np.sqrt(252)
    drawdown = (df["Close"] / df["Close"].cummax() - 1).min()

    return {
        "momentum_1y": safe(momentum_1y),
        "volatility": safe(volatility),
        "drawdown": safe(drawdown)
    }


def compute_fundamental(f):

    return {
        "pe": safe(f.get("pe"), 50),
        "pb": safe(f.get("pb"), 5),
        "roe": safe(f.get("roe"), 10),
        "debt_to_equity": safe(f.get("debt_to_equity"), 2),
        "profit_margin": safe(f.get("profit_margin"), 0.1),
        "revenue_growth": safe(f.get("revenue_growth"), 0.05),
        "dividend_yield": safe(f.get("dividend_yield"), 0)
    }


# =========================
# SCORING ENGINE
# =========================

class Scorer:

    def score(self, f, t):

        # QUALITY
        quality = (f["roe"] / 30) + (f["profit_margin"] * 2)
        quality = min(quality / 2, 1)

        # GROWTH
        growth = max(f["revenue_growth"], 0) * 10
        growth = min(growth, 1)

        # VALUE
        value = (1 / max(f["pe"], 1)) + (1 / max(f["pb"], 1))
        value = min(value * 2, 1)

        # MOMENTUM
        momentum = (t["momentum_1y"] + 1) / 2
        momentum = min(max(momentum, 0), 1)

        # FINAL SCORE
        final = (
            quality * 0.35 +
            growth * 0.25 +
            value * 0.25 +
            momentum * 0.15
        )

        return round(final * 100, 2)


# =========================
# ENGINE
# =========================

class Engine:

    def __init__(self):
        self.data = DataProvider()
        self.scorer = Scorer()

    def analyze(self, symbol):

        f = self.data.get_fundamentals(symbol)
        t = self.data.get_price(symbol)

        f = compute_fundamental(f)
        t = compute_technical(t)

        score = self.scorer.score(f, t)

        return {
            "stock": symbol,
            "score": score,
            **f,
            **t
        }

    def run(self):

        results = []

        for s in STOCKS:
            try:
                res = self.analyze(s)
                results.append(res)
            except Exception as e:
                print(f"Error {s}: {e}")

        if len(results) == 0:
            return pd.DataFrame(columns=["stock", "score"])

        df = pd.DataFrame(results)

        # FORCE SAFE COLUMN EXISTENCE
        if "score" not in df.columns:
            df["score"] = 0

        return df.sort_values("score", ascending=False)


# =========================
# STREAMLIT UI
# =========================

st.set_page_config(page_title="Quant Stock Screener", layout="wide")

st.title("📊 Quant Hedge Fund Style Stock Screener")

engine = Engine()

if st.button("Run Screener"):

    with st.spinner("Analyzing stocks..."):

        df = engine.run()

        st.subheader("Top Stocks")

        st.dataframe(df)

        st.subheader("Best Picks")

        st.write(df.head(3)[["stock", "score"]])

        st.line_chart(df.set_index("stock")["score"])
