import streamlit as st
import yfinance as yf
import pandas as pd

st.title("Stock Screener Pro (Multi-Stock)")

stocks_input = st.text_area(
    "Enter stocks (comma separated, e.g. TCS.NS, INFY.NS, RELIANCE.NS)"
)

def to_crore(x):
    try:
        return round(x / 1e7, 2)
    except:
        return None

if stocks_input:
    stocks = [s.strip() for s in stocks_input.split(",")]

    data_list = []

    for stock in stocks:
        try:
            ticker = yf.Ticker(stock)
            info = ticker.info
            hist = ticker.history(period="5y")

            price = info.get("currentPrice")
            market_cap = info.get("marketCap")
            pe = info.get("trailingPE")
            div_yield = info.get("dividendYield")

            ath = hist["Close"].max() if not hist.empty else None

            correction = None
            if price and ath:
                correction = round(((ath - price) / ath) * 100, 2)

            roe = info.get("returnOnEquity")
            debt = info.get("totalDebt")

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

            data_list.append({
                "Stock": stock,
                "Price": price,
                "MC (₹ Cr)": to_crore(market_cap),
                "PE": pe,
                "Div Yield %": round(div_yield*100,2) if div_yield else None,
                "ATH": ath,
                "Correction %": correction,
                "ROE": roe,
                "Debt (₹ Cr)": to_crore(debt),
                "FCF (₹ Cr)": to_crore(fcf),
                "FCF Yield %": fcf_yield
            })

        except:
            pass

    df = pd.DataFrame(data_list)

    st.subheader("📊 Screener Output")
    st.dataframe(df.sort_values(by="Correction %", ascending=False))
