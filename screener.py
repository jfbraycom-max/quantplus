import yfinance as yf
import pandas as pd
import requests

print("Fetching complete US stock market ticker list from the SEC...")
headers = {'User-Agent': 'PersonalScript admin@example.com'}
response = requests.get('https://www.sec.gov/files/company_tickers.json', headers=headers)
response.raise_for_status()
sec_json = response.json()
df_sec = pd.DataFrame.from_dict(sec_json, orient='index')
all_tickers = df_sec['ticker'].astype(str).str.upper().str.replace('.', '-', regex=False).unique().tolist()
print(f"Loaded {len(all_tickers)} total market tickers.")

def get_rsi(stock, period=14):
    try:
        hist = stock.history(period="3mo")['Close']
        if len(hist) < period + 1:
            return None
        delta = hist.diff()
        gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi.iloc[-1], 1)
    except Exception:
        return None

def analyze_stock(symbol):
    try:
        stock = yf.Ticker(symbol)
        financials = stock.quarterly_income_stmt
        if financials is None or financials.empty:
            return False, None

        eps_key = None
        for key in ["Normalized Diluted EPS", "Diluted EPS"]:
            if key in financials.index:
                eps_key = key
                break
        if not eps_key:
            return False, None

        eps = financials.loc[eps_key].dropna()
        if len(eps) < 5:
            return False, None

        values = eps.values
        for i in range(4):
            if values[i] <= values[i + 1]:
                return False, None

        info = stock.info
        close_price = info.get('previousClose') or info.get('regularMarketPrice')
        high_52w = info.get('fiftyTwoWeekHigh')
        rsi = get_rsi(stock, period=14)
        pct_off_52w_high = round(((close_price - high_52w) / high_52w) * 100, 1) if (close_price and high_52w) else 'N/A'

        q4_val = values[4]
        q0_val = values[0]
        growth_5q_pct = round(((q0_val - q4_val) / abs(q4_val)) * 100, 1) if q4_val != 0 else 'N/A'

        calendar = stock.calendar
        next_earnings = 'N/A'
        if calendar is not None and isinstance(calendar, dict) and 'Earnings Date' in calendar:
            e_dates = calendar['Earnings Date']
            if len(e_dates) > 0:
                next_earnings = str(e_dates[0])

        data = {
            'Ticker': symbol,
            'Name': info.get('shortName', 'N/A'),
            'Sector': info.get('sector', 'N/A'),
            'Last Close ($)': round(close_price, 2) if close_price else 'N/A',
            'RSI (14)': rsi if rsi else 'N/A',
            '% Off 52W High': pct_off_52w_high,
            '5-Qtr Growth %': growth_5q_pct,
            'Market Cap ($B)': round(info.get('marketCap', 0) / 1e9, 2) if info.get('marketCap') else 'N/A',
            'Avg Vol (M)': round(info.get('averageVolume', 0) / 1e6, 2) if info.get('averageVolume') else 'N/A',
            'Next Earnings': next_earnings,
            'Latest EPS (Q0)': round(q0_val, 2),
            'Q1 EPS': round(values[1], 2),
            'Q2 EPS': round(values[2], 2),
            'Q3 EPS': round(values[3], 2),
            'Q4 EPS': round(values[4], 2)
        }
        return True, data
    except Exception:
        return False, None

passing_results = []
print("Starting stock screening run...")
for idx, symbol in enumerate(all_tickers, 1):
    passed, stock_data = analyze_stock(symbol)
    if passed:
        print(f"[{len(passing_results)+1}] Passed: {symbol}")
        passing_results.append(stock_data)

if passing_results:
    results_df = pd.DataFrame(passing_results)
    results_df.to_csv('data/master_eps_screener_results.csv', index=False)
    print(f"Done! Saved {len(passing_results)} stocks to data/master_eps_screener_results.csv")
