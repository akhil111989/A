score = 0

# ===== QUALITY =====
if roce:
    if roce > 25:
        score += 2
    elif roce > 15:
        score += 1

# ===== GROWTH =====
if growth:
    if growth > 15:
        score += 2
    elif growth > 8:
        score += 1

# ===== FCF =====
if fcf_yield:
    if fcf_yield > 5:
        score += 2
    elif fcf_yield > 2:
        score += 1

# ===== VALUATION =====
if pe and avg_pe:
    if pe < avg_pe * 0.8:
        score += 2
    elif pe < avg_pe:
        score += 1

# ===== PRICE POSITION =====
if correction:
    if correction < -30:
        score += 2
    elif correction < -15:
        score += 1

# ===== FINAL DECISION =====
if score >= 7:
    decision = "STRONG BUY"
elif score >= 5:
    decision = "BUY"
elif score >= 3:
    decision = "HOLD"
else:
    decision = "SELL"
