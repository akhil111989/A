import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.title("Ultimate Stock Screener (All-in-One)")

stocks_input = st.text_area(
    "Enter stocks (comma separated, e.g. TCS.NS, INFY.NS, RELIANCE.NS)"
)

def to_crore(x):
    try:
        return round(x / 1e7, 2)
    except:
        return None

# 🔹 Screener Data Function
def get_screener_data(stock_name):
    try:
        url = f"https://www.screener.in/company/{stock_name}/"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        ratios = {}

        for li in soup.select("ul#top-ratios li"):
            name = li.select_one("span.name").text.strip()
            value = li.select_one("span.number").text.strip()
            ratios[name] = value

        return {
            "ROCE": ratios.get("Return on capital employed"),
            "ROE": ratios.get("Return on equity"),
            "PE_alt": ratios.get("P/E"),
            "Dividend_alt": ratios.get("Dividend Yield"),
        }
    except:
        return {}

if stocks_input:
    stocks = [s.strip() for s in stocks_input.split(",")]

    results = []

    for i, stock in enumerate(stocks, start=1):
        try:
            ticker = yf.Ticker(stock)
            info = ticker.info
            hist = ticker.history(period="5y")

            screener = get_screener_data(stock.replace(".NS",""))

            price = info.get("currentPrice")
            market_cap = info.get("marketCap")
            pe = info.get("trailingPE")
            div_yield = info.get("dividendYield")

            # ATH price
            ath_price = hist["Close"].max() if not hist.empty else None

            # ATH market cap
            ath_mc = None
            if ath_price and price and market_cap:
                ath_mc = (ath_price / price) * market_cap

            # Correction %
            correction = None
            if ath_price and price:
                correction = round(((ath_price - price) / ath_price) * 100, 2)

            # FCF
            fcf = None
            fcf_yield = None
            try:
                cf = ticker.cashflow
                fcf = cf.loc["Free Cash Flow"][0]
                if market_cap and fcf:
                    fcf_yield = round((fcf / market_cap) * 100, 2)
            except:
                pass

            # Margins
            margin = info.get("profitMargins")

            # Basic Decision Logic
            decision = "HOLD"
            if correction and correction > 30 and fcf_yield and fcf_yield > 5:
                decision = "BUY"
            elif correction and correction < 10:
                decision = "SELL"

            results.append({
                "S.No": i,
                "Stock": stock,
                "Price": price,
                "MC (₹ Cr)": to_crore(market_cap),
                "ATH Price": ath_price,
                "ATH MC (₹ Cr)": to_crore(ath_mc),
                "Correction %": correction,
                "FCF (₹ Cr)": to_crore(fcf),
                "FCF Yield %": fcf_yield,
                "PE (Yahoo)": pe,
                "PE (Screener)": screener.get("PE_alt"),
                "ROCE": screener.get("ROCE"),
                "ROE": screener.get("ROE"),
                "Margins": margin,
                "Dividend %": round(div_yield*100,2) if div_yield else screener.get("Dividend_alt"),
                "Decision": decision
            })

        except:
            pass

    df = pd.DataFrame(results)

    st.subheader("📊 Screener Output")
    st.dataframe(df)
