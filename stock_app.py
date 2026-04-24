import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time

@st.cache_data(ttl=3600)
def get_stock_data(ticker):

    for attempt in range(3):  # retry logic
        try:
            stock = yf.Ticker(ticker)

            hist = stock.history(period="5y")

            if hist.empty:
                return None, None

            # PRICE DATA
            ath = hist["High"].max()
            atl = hist["Low"].min()

            ath_date = hist["High"].idxmax().date()
            atl_date = hist["Low"].idxmin().date()

            current_price = hist["Close"].iloc[-1]

            correction = round((ath - current_price) / ath * 100, 2)

            # SAFE INFO FETCH (no .info)
            try:
                info = stock.get_info()
            except:
                info = {}

            market_cap = info.get("marketCap", None)
            if market_cap:
                market_cap = round(market_cap / 1e7, 2)  # crores

            pe = info.get("trailingPE", None)

            div_yield = info.get("dividendYield", None)
            if div_yield:
                div_yield *= 100

            roce = info.get("returnOnEquity", None)
            if roce:
                roce *= 100

            # FCF
            try:
                fcf = stock.cashflow.loc["Free Cash Flow"].iloc[0]
                fcf = round(fcf / 1e7, 2)
            except:
                fcf = None

            earnings_date = info.get("earningsDate", None)
            div_date = info.get("exDividendDate", None)

            return {
                "current_price": current_price,
                "ath": ath,
                "ath_date": ath_date,
                "atl": atl,
                "atl_date": atl_date,
                "correction_pct": correction,
                "market_cap": market_cap,
                "pe": pe,
                "roce": roce,
                "dividend_yield": div_yield,
                "fcf": fcf,
                "earnings_date": earnings_date,
                "dividend_date": div_date
            }, hist

        except Exception as e:
            if attempt < 2:
                time.sleep(1)
                continue
            return None, None
