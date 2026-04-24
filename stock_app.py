# ==============================
# QUANT HEDGE FUND STYLE SYSTEM
# ==============================

import pandas as pd
import numpy as np
import yfinance as yf
from dataclasses import dataclass
import warnings
warnings.filterwarnings("ignore")


# =========================================================
# 1. DATA LAYER (LIVE MARKET DATA)
# =========================================================

class YahooDataProvider:

    def get_price_data(self, symbol, period="5y"):
        df = yf.download(symbol + ".NS", period=period, interval="1d", progress=False)
        df.dropna(inplace=True)
        return df

    def get_fundamentals(self, symbol):

        t = yf.Ticker(symbol + ".NS")
        info = t.info

        return {
            "pe": info.get("trailingPE", np.nan),
            "pb": info.get("priceToBook", np.nan),
            "roe": info.get("returnOnEquity", np.nan),
            "debt_to_equity": info.get("debtToEquity", np.nan),
            "profit_margin": info.get("profitMargins", np.nan),
            "revenue_growth": info.get("revenueGrowth", np.nan),
            "dividend_yield": info.get("dividendYield", 0) or 0
        }


# =========================================================
# 2. FEATURE ENGINEERING
# =========================================================

def compute_technical_features(df):

    df["returns"] = df["Close"].pct_change()

    features = {
        "momentum_3m": (df["Close"].iloc[-1] / df["Close"].iloc[-60] - 1),
        "momentum_1y": (df["Close"].iloc[-1] / df["Close"].iloc[-252] - 1),
        "volatility": df["returns"].std() * np.sqrt(252),
        "max_drawdown": (df["Close"] / df["Close"].cummax() - 1).min(),
        "price_vs_52w_high": df["Close"].iloc[-1] / df["Close"].max()
    }

    return features


def compute_fundamental_features(f):

    return {
        "pe": f["pe"],
        "pb": f["pb"],
        "roe": f["roe"],
        "debt_to_equity": f["debt_to_equity"],
        "profit_margin": f["profit_margin"],
        "revenue_growth": f["revenue_growth"],
        "dividend_yield": f["dividend_yield"]
    }


# =========================================================
# 3. MULTI-FACTOR SCORING ENGINE
# =========================================================

@dataclass
class Weights:
    quality: float = 0.35
    growth: float = 0.25
    value: float = 0.25
    momentum: float = 0.15


class FactorModel:

    def score(self, f, t):

        # ------------------
        # QUALITY SCORE
        # ------------------
        quality = (
            min(f["roe"] / 30, 1) * 0.6 +
            min(f["profit_margin"] / 0.3, 1) * 0.4
        )

        # ------------------
        # GROWTH SCORE
        # ------------------
        growth = (
            max(f["revenue_growth"], 0) * 0.5 +
            min(f["profit_margin"], 1) * 0.5
        )

        # ------------------
        # VALUE SCORE
        # ------------------
        value = (
            (1 / max(f["pe"], 1)) * 0.5 +
            (1 / max(f["pb"], 1)) * 0.5
        )
        value = min(value * 10, 1)

        # ------------------
        # MOMENTUM SCORE
        # ------------------
        momentum = (
            max(t["momentum_3m"], -1) * 0.4 +
            max(t["momentum_1y"], -1) * 0.6
        )

        momentum = (momentum + 1) / 2  # normalize

        # ------------------
        # FINAL SCORE
        # ------------------
        final = (
            quality * 0.35 +
            growth * 0.25 +
            value * 0.25 +
            momentum * 0.15
        )

        return round(final * 100, 2)


# =========================================================
# 4. STOCK UNIVERSE
# =========================================================

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


# =========================================================
# 5. RESEARCH ENGINE
# =========================================================

class ResearchEngine:

    def __init__(self):
        self.data = YahooDataProvider()
        self.model = FactorModel()

    def analyze_stock(self, symbol):

        try:
            price_df = self.data.get_price_data(symbol)
            fund = self.data.get_fundamentals(symbol)

            if price_df.empty:
                return None

            tech = compute_technical_features(price_df)
            fund_feat = compute_fundamental_features(fund)

            score = self.model.score(fund_feat, tech)

            return {
                "stock": symbol,
                "score": score,
                **fund_feat,
                **tech
            }

        except Exception as e:
            print(f"Error for {symbol}: {e}")
            return None

    def run(self):

        results = []

        for s in STOCKS:
            res = self.analyze_stock(s)
            if res:
                results.append(res)

        df = pd.DataFrame(results)
        return df.sort_values("score", ascending=False)


# =========================================================
# 6. SIMPLE BACKTEST ENGINE
# =========================================================

class Backtester:

    def __init__(self, engine):
        self.engine = engine

    def run(self):

        df = self.engine.run()

        top = df.head(3)["stock"].tolist()

        print("\nTOP PICKS:", top)

        returns = []

        for stock in top:

            data = yf.download(stock + ".NS", period="1y", progress=False)
            if data.empty:
                continue

            ret = data["Close"].pct_change().mean() * 252
            returns.append(ret)

        portfolio_return = np.mean(returns) if returns else 0

        print("\nExpected Portfolio Return (approx):", round(portfolio_return * 100, 2), "%")


# =========================================================
# 7. PORTFOLIO CONSTRUCTION
# =========================================================

def build_portfolio(df, top_n=5):

    top = df.head(top_n).copy()

    top["weight"] = top["score"] / top["score"].sum()

    return top[["stock", "score", "weight"]]


# =========================================================
# 8. MAIN EXECUTION
# =========================================================

if __name__ == "__main__":

    engine = ResearchEngine()

    print("\nRUNNING QUANT RESEARCH ENGINE...\n")

    df = engine.run()

    print("\n=== RANKING ===\n")
    print(df[["stock", "score", "pe", "roe", "momentum_1y"]])

    portfolio = build_portfolio(df)

    print("\n=== PORTFOLIO ===\n")
    print(portfolio)

    backtester = Backtester(engine)
    backtester.run()
