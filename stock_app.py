def analyze(symbol):
    try:
        yf_symbol = symbol + ".NS"
        stock = yf.Ticker(yf_symbol)

        hist = stock.history(period="5y")

        if hist.empty:
            return None

        # ===== PRICE (RELIABLE) =====
        price = hist["Close"].dropna().iloc[-1]
        ath = hist["Close"].max()
        correction = ((price - ath) / ath) * 100

        # ===== SCREENER DATA (RELIABLE) =====
        sc = get_screener(symbol)

        pe = sc.get("PE", np.nan)
        roce = sc.get("ROCE", np.nan)
        dividend = sc.get("Dividend", np.nan)
        mcap_cr = sc.get("MarketCap", np.nan)  # already in Cr

        # ===== DERIVE SHARES =====
        shares = (mcap_cr * 1e7) / price if mcap_cr and price else np.nan

        # ===== ATH MARKET CAP =====
        ath_mcap = ath * shares / 1e7 if shares else np.nan

        # ===== FCF (BEST EFFORT) =====
        try:
            cf = stock.cashflow
            fcf = cf.loc["Total Cash From Operating Activities"][0] - cf.loc["Capital Expenditures"][0]
            fcf_cr = fcf / 1e7
        except:
            fcf_cr = np.nan

        fcf_yield = (fcf_cr / mcap_cr * 100) if mcap_cr and fcf_cr else np.nan

        # ===== GROWTH =====
        try:
            info = stock.info
            growth = info.get("earningsGrowth", np.nan)
            growth = growth * 100 if growth else np.nan
        except:
            growth = np.nan

        # ===== DEBT =====
        try:
            debt = info.get("totalDebt", np.nan) / 1e7
        except:
            debt = np.nan

        # ===== SCORE =====
        score = 0
        if correction < -25: score += 2
        if fcf_yield and fcf_yield > 3: score += 2
        if roce and roce > 18: score += 2
        if growth and growth > 10: score += 1
        if debt and mcap_cr and debt < mcap_cr * 0.5: score += 1

        if score >= 6:
            decision = "STRONG BUY"
        elif score >= 4:
            decision = "BUY"
        elif score >= 2:
            decision = "HOLD"
        else:
            decision = "SELL"

        return {
            "Stock": symbol,
            "Price": price,
            "MCap (Cr)": mcap_cr,
            "ATH": ath,
            "ATH MCap (Cr)": ath_mcap,
            "Correction %": correction,
            "FCF (Cr)": fcf_cr,
            "FCF Yield %": fcf_yield,
            "PE": pe,
            "ROCE %": roce,
            "Growth %": growth,
            "Dividend %": dividend,
            "Debt (Cr)": debt,
            "Score": score,
            "Decision": decision
        }

    except Exception as e:
        return None
