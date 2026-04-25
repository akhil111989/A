# 📊 Indian Stock Intelligence Dashboard

A real-time Streamlit dashboard aggregating Indian stock data from **three independent sources** for accuracy.

---

## ✅ Features

| Metric | Source |
|--------|--------|
| ATH / ATL + dates | Yahoo Finance (full history) |
| Market Cap (₹ Crores) | Yahoo Finance |
| Correction % from ATH | Calculated |
| Free Cash Flow + FCF Yield | Yahoo Finance |
| PE + 5-Year Average PE | Yahoo Finance + Screener.in |
| ROCE + 5Y Growth | Screener.in |
| Dividend Yield | Yahoo Finance |
| Next Result Date | NSE India API + Yahoo Finance |
| Dividend Ex-Date | NSE India API + Yahoo Finance |
| ROE, P/B, Beta, EPS Growth | Yahoo Finance |

---

## 🚀 Deploy to Streamlit Cloud (Free)

### Step 1 — Fork or create a GitHub repo
1. Go to [github.com](https://github.com) → **New Repository**
2. Name it e.g. `indian-stock-dashboard`
3. Set it to **Public**

### Step 2 — Upload files
Upload both files to the root of your repo:
- `app.py`
- `requirements.txt`

Or via git:
```bash
git clone https://github.com/YOUR_USERNAME/indian-stock-dashboard.git
cd indian-stock-dashboard
# copy app.py and requirements.txt here
git add .
git commit -m "Initial commit"
git push origin main
```

### Step 3 — Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **New app**
4. Select your repo → branch: `main` → file: `app.py`
5. Click **Deploy** 🎉

Your app will be live at:
`https://YOUR_USERNAME-indian-stock-dashboard-app-XXXXX.streamlit.app`

---

## 💻 Run Locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/indian-stock-dashboard.git
cd indian-stock-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

---

## 🗂️ File Structure

```
indian-stock-dashboard/
├── app.py             ← Main Streamlit application
├── requirements.txt   ← Python dependencies
└── README.md          ← This file
```

---

## 📡 Data Sources

| Source | What it provides | Cache TTL |
|--------|-----------------|-----------|
| **Yahoo Finance** (`yfinance`) | Price, ATH/ATL, FCF, PE, Market Cap, Dividends, Earnings Date | 15 min |
| **Screener.in** | ROCE, 5-Year Average PE, ROCE growth trend | 1 hour |
| **NSE India API** | Corporate actions, result board meeting dates, dividend ex-dates | 30 min |

---

## 📝 Supported Symbols

Enter **NSE ticker symbols** (without `.NS` suffix):

```
RELIANCE   TCS        INFY       HDFCBANK   ICICIBANK
WIPRO      ITC        BHARTIARTL MARUTI     SUNPHARMA
TATAMOTORS AXISBANK   KOTAKBANK  BAJFINANCE LT
ADANIGREEN ADANIPORTS NESTLEIND  ASIANPAINT HINDUNILVR
```

---

## ⚠️ Disclaimers

- **Educational use only** — Not financial advice
- Screener.in scraping may occasionally fail due to rate limits or page structure changes; ROCE and 5Y PE will show N/A in that case
- NSE API requires a brief warm-up (cookie handshake); result/dividend dates may not always be available
- Always verify data with official NSE/BSE sources before making investment decisions

---

## 🛠️ Troubleshooting

| Issue | Fix |
|-------|-----|
| `Symbol not found` | Check NSE symbol spelling (no `.NS` suffix needed) |
| ROCE shows N/A | Screener.in may be rate-limiting; wait and retry |
| Result date shows "Check NSE" | NSE calendar may not have future dates yet |
| App is slow on first load | Normal — downloading historical data; subsequent loads use cache |

---

*Built with ❤️ using Streamlit · yfinance · Screener.in · NSE India*
