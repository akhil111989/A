def analyze(symbol):
    try:
        import yfinance as yf
        import numpy as np

        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="max").dropna()

        # ===== PRICE =====
        price = hist["Close"].iloc[-1]

        ath_price = hist["Close"].max()
        ath_date = hist["Close"].idxmax()

        atl_price = hist["Close"].min()
        atl_date = hist["Close"].idxmin()

        ath_date = ath_date.strftime("%d-%b-%Y")
        atl_date = atl_date.strftime("%d-%b-%Y")

        correction = ((price - ath_price) / ath_price) * 100

        # ===== PE (current + avg approx) =====
        info = ticker.info
        pe = info.get("trailingPE", None)

        try:
            avg_pe = (hist["Close"] / (price / pe)).mean() if pe else None
        except:
            avg_pe = None

        # ===== DIVIDEND =====
        dividend = info.get("dividendYield", None)
        if dividend:
            dividend *= 100

        # ===== RESULT + DIV DATE =====
        try:
            cal = ticker.calendar
            result_date = str(cal.loc["Earnings Date"][0].date())
        except:
            result_date = "NA"

        try:
            dividend_date = str(cal.loc["Ex-Dividend Date"][0].date())
        except:
            dividend_date = "NA"

        # ===== SCORE ENGINE =====
        score = 0

        if correction < -40:
            score += 3
        elif correction < -25:
            score += 2
        elif correction < -15:
            score += 1

        if pe and avg_pe and pe < avg_pe:
            score += 1

        decision = "STRONG BUY" if score >= 4 else "BUY" if score == 3 else "HOLD" if score == 2 else "AVOID"

        return {
            "Stock": symbol,
            "Price": price,

            "ATH Price": ath_price,
            "ATH Date": ath_date,

            "ATL Price": atl_price,
            "ATL Date": atl_date,

            "Correction %": correction,

            "PE": pe,
            "Avg PE": avg_pe,

            "Dividend %": dividend,

            "Result Date": result_date,
            "Dividend Record Date": dividend_date,

            "Score": score,
            "Decision": decision
        }

    except Exception as e:
        return {"Stock": symbol, "Error": str(e)}
