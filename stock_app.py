def calculate_investment_score(ticker, roce, growth, fcf_yield, pe, avg_pe, correction):
    score = 0
    
    # 1. QUALITY (ROCE)
    if roce is not None:
        if roce > 25:
            score += 2
        elif roce > 15:
            score += 1

    # 2. GROWTH
    if growth is not None:
        if growth > 15:
            score += 2
        elif growth > 8:
            score += 1

    # 3. FCF YIELD
    if fcf_yield is not None:
        if fcf_yield > 5:
            score += 2
        elif fcf_yield > 2:
            score += 1

    # 4. VALUATION (Relative PE)
    if pe and avg_pe:
        if pe < (avg_pe * 0.8):
            score += 2
        elif pe < avg_pe:
            score += 1

    # 5. PRICE POSITION (Correction from High)
    if correction is not None:
        if correction < -30:
            score += 2
        elif correction < -15:
            score += 1

    # FINAL DECISION LOGIC
    if score >= 7:
        decision = "STRONG BUY"
    elif score >= 5:
        decision = "BUY"
    elif score >= 3:
        decision = "HOLD"
    else:
        decision = "SELL"
        
    return {
        "ticker": ticker,
        "total_score": score,
        "decision": decision
    }

# --- EXAMPLE USAGE ---
stock_data = {
    "ticker": "TECH_CORP",
    "roce": 28,        # +2
    "growth": 12,      # +1
    "fcf_yield": 6,    # +2
    "pe": 18,          
    "avg_pe": 25,      # +2 (18 is < 80% of 25)
    "correction": -10  # +0
}

result = calculate_investment_score(**stock_data)

print(f"Analysis for {result['ticker']}:")
print(f"Final Score: {result['total_score']}/10")
print(f"Action: {result['decision']}")
