import pandas as pd
import numpy as np
import requests
from dataclasses import dataclass

# =========================
# 1. DATA LAYER (PLUGGABLE)
# =========================

class DataProvider:
    """Base class for all data sources"""
    def get_fundamentals(self, symbol: str) -> dict:
        raise NotImplementedError


class MockScreener(DataProvider):
    """Replace with Screener.in scraping or API"""
    def get_fundamentals(self, symbol: str):
        return {
            "pe": np.random.uniform(5, 40),
            "pb": np.random.uniform(0.5, 8),
            "roe": np.random.uniform(5, 35),
            "roce": np.random.uniform(5, 40),
            "debt_to_equity": np.random.uniform(0, 3),
            "revenue_cagr_5y": np.random.uniform(-5, 35),
            "profit_cagr_5y": np.random.uniform(-10, 40),
            "dividend_yield": np.random.uniform(0, 5),
            "current_price": np.random.uniform(50, 3000),
            "ath_price": np.random.uniform(100, 5000),
            "atl_price": np.random.uniform(10, 500)
        }


# =========================
# 2. FEATURE ENGINEERING
# =========================

def compute_features(data: dict) -> dict:
    return {
        **data,
        "discount_from_ath": (data["ath_price"] - data["current_price"]) / data["ath_price"],
        "upside_from_atl": (data["current_price"] - data["atl_price"]) / data["atl_price"]
    }


# =========================
# 3. SCORING ENGINE
# =========================

@dataclass
class Weights:
    quality: float = 0.35
    growth: float = 0.25
    value: float = 0.25
    risk: float = 0.15


class StockScorer:

    def __init__(self, weights=Weights()):
        self.w = weights

    def score(self, f: dict) -> float:

        # QUALITY SCORE (ROE, ROCE)
        quality = (
            (f["roe"] / 35) * 0.5 +
            (f["roce"] / 40) * 0.5
        )

        # GROWTH SCORE
        growth = (
            max(f["revenue_cagr_5y"], 0) / 35 * 0.5 +
            max(f["profit_cagr_5y"], 0) / 40 * 0.5
        )

        # VALUE SCORE
        value = (
            (1 / max(f["pe"], 1)) * 0.5 +
            (1 / max(f["pb"], 1)) * 0.5
        )
        value = min(value * 10, 1)  # normalize

        # RISK PENALTY
        risk = (
            (1 - min(f["debt_to_equity"] / 2, 1)) * 0.6 +
            f["dividend_yield"] / 5 * 0.4
        )

        final_score = (
            quality * self.w.quality +
            growth * self.w.growth +
            value * self.w.value +
            risk * self.w.risk
        )

        return round(final_score * 100, 2)


# =========================
# 4. STOCK UNIVERSE
# =========================

STOCKS = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "LT", "TATAMOTORS", "ITC"]


# =========================
# 5. PIPELINE ENGINE
# =========================

class Screener:

    def __init__(self, provider, scorer):
        self.provider = provider
        self.scorer = scorer

    def run(self):

        results = []

        for stock in STOCKS:

            raw = self.provider.get_fundamentals(stock)
            features = compute_features(raw)
            score = self.scorer.score(features)

            results.append({
                "stock": stock,
                "score": score,
                **features
            })

        df = pd.DataFrame(results)
        return df.sort_values("score", ascending=False)


# =========================
# 6. EXECUTION
# =========================

if __name__ == "__main__":

    provider = MockScreener()
    scorer = StockScorer()

    screener = Screener(provider, scorer)
    df = screener.run()

    print("\n=== HEDGE FUND STYLE RANKING ===\n")
    print(df[["stock", "score", "pe", "roe", "roce", "profit_cagr_5y"]])
