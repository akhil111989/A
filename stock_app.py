import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(layout="wide")
st.title("🏦 Institutional Stock Screener")

stocks_input = st.text_area(
    "Enter stocks (comma separated, e.g. TCS.NS, INFY.NS, RELIANCE.NS)"
)

# 🔹 Formatting helpers
def to_crore(x):
    try:
        return round(x / 1e7, 1)
    except:
        return None

def pct(x):
    try:
        return round(x * 100, 1)
    except:
        return None

def r1(x):
    try:
        return round(x, 1)
    except:
        return None

# 🔹 Screener Data
def get_screener(stock):
    try:
        url = f"https://www.screener.in/company/{stock}/"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        ratios = {}
        for li in soup.select("ul#top-ratios li"):
            name = li.select_one("span.name").text.strip()
            val = li.select_one("span.number").text.strip()
            ratios[name] = val

        growth = {}
        for row in soup.select("table.data-table tbody tr"):
            cols = [c.text.strip() for c in row.find_all("td")]
            if len(cols) >= 2:
                growth[cols[0]] = cols[-1]

        return ratios, growth
    except:
        return {}, {}

# 🔹 Trend
def trend_flag(val):
    try:
        v = float(val.replace("%",""))
        if v > 20:
            return "↑ Strong"
        elif v > 12:
            return "→ Stable"
        else:
            return "↓ Weak"
    except:
        return None

if stocks_input:
    stocks = [s.strip() for s in stocks_input.split(",")]

    rows = []

    for i, stock in enumerate(stocks, 1):
        try:
            t = yf.Ticker(stock)
            info = t.info
            hist = t.history(period="5y")

            ratios, growth = get_screener(stock.replace(".NS",""))

            price = r1(info.get("currentPrice"))
            mc = to_crore(info.get("marketCap"))
            pe = r1(info.get("trailingPE"))
            margin = pct(info.get("profitMargins"))

            # Dividend %
            div = info.get("dividendYield")
            div = pct(div) if div else ratios.get("Dividend Yield")

            # ATH
            ath_price = hist["Close"].max() if not hist.empty else None
            ath_price = r1(ath_price)

            ath_mc = None
            if ath_price and price and mc:
                ath_mc = r1((ath_price/price)*mc)

            corr = None
            if ath_price and price:
                corr = r1(((ath_price-price)/ath_price)*100)

            # FCF
            fcf, fcf_y = None, None
            try:
                cf = t.cashflow
                fcf = to_crore(cf.loc["Free Cash Flow"][0])
                if mc and fcf:
                    fcf_y = r1((fcf/(mc))*100)
            except:
                pass

            # PE history
            pe_avg, pe_ath = None, None
            try:
                eps = info.get("trailingEps")
                if eps and not hist.empty:
                    pe_series = hist["Close"]/eps
                    pe_avg = r1(pe_series.mean())
                    pe_ath = r1(pe_series.max())
            except:
                pass

            roce = ratios.get("Return on capital employed")

            # 🔥 Score
            score = 0
            if corr and corr > 25: score += 1
            if pe and pe_avg and pe < pe_avg: score += 1
            try:
                if float(roce.replace("%","")) > 18: score += 1
            except: pass
            if margin and margin > 15: score += 1
            if fcf_y and fcf_y > 5: score += 1
            if growth.get("Profit Growth"): score += 1

            if score >= 5:
                decision = "🟢 STRONG BUY"
            elif score >= 3:
                decision = "🟡 BUY"
            elif score == 2:
                decision = "⚪ HOLD"
            else:
                decision = "🔴 AVOID"

            rows.append({
                "S.No": i,
                "Stock": stock,
                "Price": price,
                "MC (₹ Cr)": mc,
                "ATH Price": ath_price,
                "ATH MC": ath_mc,
                "Corr %": corr,
                "PE": pe,
                "PE Avg": pe_avg,
                "PE ATH": pe_ath,
                "ROCE": roce,
                "ROCE Trend": trend_flag(roce),
                "Margins %": margin,
                "Profit Growth": growth.get("Profit Growth"),
                "FCF (₹ Cr)": fcf,
                "FCF Yield %": fcf_y,
                "Dividend %": div,
                "Score": score,
                "Decision": decision
            })

        except:
            pass

    df = pd.DataFrame(rows)

    st.subheader("📊 Institutional Screener Output")

    def style(val):
        if "STRONG BUY" in str(val): return "background-color:#90ee90"
        if "BUY" in str(val): return "background-color:#fff3cd"
        if "AVOID" in str(val): return "background-color:#f8d7da"
        return ""

    st.dataframe(df.style.applymap(style, subset=["Decision"]), use_container_width=True)

    st.download_button(
        "📥 Download Excel",
        df.to_csv(index=False),
        "screener.csv",
        "text/csv"
    )
