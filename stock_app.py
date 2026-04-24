import yfinance as yf
import pandas as pd
import numpy as np

# ======================
# STOCK LIST
# ======================
stocks = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS"
]

# ======================
# ANALYZE FUNCTION
# ======================
def analyze(symbol):

    t = yf.Ticker(symbol)
    info = t.info
    hist = t.history(period="max")

    hist = hist.dropna()

    price = hist["Close"].iloc[-1]

    ath = hist["Close"].max()
    atl = hist["Close"].min()

    ath_date = hist["Close"].idxmax().strftime("%d-%b-%Y")
    atl_date = hist["Close"].idxmin().strftime("%d-%b-%Y")

    correction = ((price - ath) / ath) * 100

    # ======================
    # FUNDAMENTALS
    # ======================
    pe = info.get("trailingPE")
    roe = info.get("returnOnEquity")
    growth = info.get("earningsGrowth")
    dividend = info.get("dividendYield")
    debt = info.get("debtToEquity")

    if roe: roe *= 100
    if dividend: dividend *= 100

    # ======================
    # EVENTS
    # ======================
    cal = t.calendar

    try:
        result_date = str(cal.loc["Earnings Date"][0].date())
    except:
        result_date = "NA"

    try:
        ex_div = str(cal.loc["Ex-Dividend Date"][0].date())
    except:
        ex_div = "NA"

    # ======================
    # SIMPLE SCORE (YOUR ORIGINAL IDEA, CLEANED)
    # ======================
    score = 0

    if roe and roe > 15:
        score += 1

    if growth and growth > 8:
        score += 1

    if pe and pe < 25:
        score += 1

    if correction and correction < -20:
        score += 1

    if debt and debt < 50:
        score += 1

    # ======================
    # FINAL DECISION
    # ======================
    if score >= 4:
        decision = "BUY"
    elif score == 3:
        decision = "HOLD"
    else:
        decision = "SELL"

    return {
        "Stock": symbol,
        "Price": price,
        "ATH": ath,
        "ATH Date": ath_date,
        "ATL": atl,
        "ATL Date": atl_date,
        "Correction %": correction,
        "PE": pe,
        "ROE %": roe,
        "Growth %": growth,
        "Debt": debt,
        "Dividend %": dividend,
        "Result Date": result_date,
        "Ex-Dividend": ex_div,
        "Score": score,
        "Decision": decision
    }

# ======================
# RUN
# ======================
df = pd.DataFrame([analyze(s) for s in stocks])

print(df)
