import yfinance as yf
import pandas as pd
import numpy as np

# =========================
# STOCK LIST
# =========================
stocks = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ITC.NS"
]

# =========================
# FETCH DATA
# =========================
def get_stock(symbol):

    t = yf.Ticker(symbol)
    info = t.info
    hist = t.history(period="max").dropna()

    price = hist["Close"].iloc[-1]

    ath = hist["Close"].max()
    atl = hist["Close"].min()

    ath_date = hist["Close"].idxmax().strftime("%d-%b-%Y")
    atl_date = hist["Close"].idxmin().strftime("%d-%b-%Y")

    correction = (price - ath) / ath * 100

    return {
        "symbol": symbol,
        "price": price,
        "pe": info.get("trailingPE"),
        "roe": info.get("returnOnEquity"),
        "growth": info.get("earningsGrowth"),
        "debt": info.get("debtToEquity"),
        "margin": info.get("profitMargins"),
        "ath": ath,
        "atl": atl,
        "ath_date": ath_date,
        "atl_date": atl_date,
        "correction": correction
    }

# =========================
# NORMALIZATION (IMPORTANT)
# =========================
def zscore(x):
    return (x - np.mean(x)) / (np.std(x) + 1e-9)

# =========================
# BUILD DATAFRAME
# =========================
data = [get_stock(s) for s in stocks]
df = pd.DataFrame(data)

# fill missing values safely
df["roe"] = df["roe"].fillna(0) * 100
df["growth"] = df["growth"].fillna(0)
df["debt"] = df["debt"].fillna(0)
df["margin"] = df["margin"].fillna(0)
df["pe"] = df["pe"].fillna(df["pe"].median())

# =========================
# FACTOR ENGINE (ELITE MODEL)
# =========================

# VALUE (cheaper is better)
df["value_score"] = -zscore(df["pe"])

# QUALITY (ROE + margin)
df["quality_score"] = zscore(df["roe"]) + zscore(df["margin"])

# GROWTH
df["growth_score"] = zscore(df["growth"])

# MOMENTUM (deep correction = opportunity)
df["momentum_score"] = -zscore(df["correction"])

# RISK (lower debt = better)
df["risk_score"] = -zscore(df["debt"])

# =========================
# FINAL SCORE (ELITE WEIGHTS)
# =========================
df["score"] = (
    0.25 * df["value_score"] +
    0.25 * df["quality_score"] +
    0.20 * df["growth_score"] +
    0.15 * df["momentum_score"] +
    0.15 * df["risk_score"]
)

# =========================
# DECISION ENGINE
# =========================
df["signal"] = pd.qcut(
    df["score"],
    q=3,
    labels=["SELL", "HOLD", "STRONG BUY"]
)

# rank
df["rank"] = df["score"].rank(ascending=False)

# =========================
# OUTPUT
# =========================
print(df[[
    "symbol",
    "score",
    "rank",
    "signal",
    "price",
    "pe",
    "roe",
    "growth",
    "debt",
    "correction",
    "ath_date",
    "atl_date"
]])
