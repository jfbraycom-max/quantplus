import requests
import yfinance as yf
from app.database import SessionLocal
import app.models as models

def get_sec_tickers():
    """Fetch complete list of SEC-registered US stock tickers."""
    headers = {'User-Agent': 'QuantPlus Screener admin@quantplus.local'}
    url = 'https://www.sec.gov/files/company_tickers.json'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        tickers = [item['ticker'].replace('.', '-') for item in data.values()]
        return tickers
    except Exception as e:
        print(f"Error fetching SEC tickers: {e}")
        return []

def evaluate_tier1_turnaround(eps_values):
    """
    Tier 1 Rules:
    - 5 quarters available (Q0=latest, Q1, Q2, Q3, Q4=oldest)
    - Last 2 quarters (Q0, Q1) MUST be positive (> 0)
    - Q4 -> Q3 -> Q2 -> Q1 -> Q0 must show continuous step-by-step growth
    - Q2, Q3, Q4 are allowed to be negative if continuously improving
    """
    if len(eps_values) < 5:
        return False
    
    q0, q1, q2, q3, q4 = eps_values[0], eps_values[1], eps_values[2], eps_values[3], eps_values[4]
    
    # Last 2 quarters must be strictly positive
    if q0 <= 0 or q1 <= 0:
        return False
        
    # Continuous 5-quarter improvement
    if not (q0 > q1 > q2 > q3 > q4):
        return False
        
    return True

def evaluate_tier2_watch(eps_values):
    """
    Tier 2 Rules:
    - At least 3 quarters available
    - Last 2 quarters show positive QoQ growth (Q0 > Q1 > Q2 > 0)
    """
    if len(eps_values) < 3:
        return False
    
    q0, q1, q2 = eps_values[0], eps_values[1], eps_values[2]
    return q0 > q1 > q2 and q0 > 0 and q1 > 0

def evaluate_seasonal_yoy(eps_values):
    """
    Seasonal Rule:
    - Compares current quarter (Q0) to same quarter last year (Q4)
    """
    if len(eps_values) < 5:
        return False
    return eps_values[0] > eps_values[4] and eps_values[0] > 0

def run_screener_job(limit_tickers=None):
    """Executes the complete market scan and updates SQLite database."""
    db = SessionLocal()
    tickers = get_sec_tickers()
    
    if limit_tickers:
        tickers = tickers[:limit_tickers]
        
    print(f"Starting QuantPlus Screener scan across {len(tickers)} tickers...")
    
    passed_count = 0
    for symbol in tickers:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Filter 1: Major US Exchanges & Liquidity
            exchange = info.get('exchange', '')
            mcap = info.get('marketCap', 0) / 1e9 if info.get('marketCap') else 0
            avg_vol = info.get('averageVolume', 0) / 1e6 if info.get('averageVolume') else 0
            
            if exchange not in ['NYS', 'NASDAQ', 'NYQ', 'NMS', 'ASE', 'AMX']:
                continue
            if mcap < 1.0 or avg_vol < 1.0:  # Minimum $1B Market Cap & 1M Volume
                continue

            # Fetch Financials
            financials = stock.quarterly_income_stmt
            if financials is None or financials.empty:
                continue
                
            eps_key = None
            for key in ["Normalized Diluted EPS", "Diluted EPS"]:
                if key in financials.index:
                    eps_key = key
                    break
            if not eps_key:
                continue
                
            eps_series = financials.loc[eps_key].dropna()
            eps_values = eps_series.values
            
            # Screening Rule Evaluations
            is_tier1 = evaluate_tier1_turnaround(eps_values)
            is_tier2 = evaluate_tier2_watch(eps_values) if not is_tier1 else False
            is_seasonal = evaluate_seasonal_yoy(eps_values) if not (is_tier1 or is_tier2) else False
            
            if not (is_tier1 or is_tier2 or is_seasonal):
                continue
                
            tier_label = "5_QTR_TURNAROUND" if is_tier1 else ("2_QTR_WATCH" if is_tier2 else "SEASONAL_YOY")
            
            close_price = info.get('previousClose') or info.get('regularMarketPrice') or 0
            high_52w = info.get('fiftyTwoWeekHigh') or close_price
            pct_off_52w = round(((close_price - high_52w) / high_52w) * 100, 1) if high_52w else 0
            
            q0_val = eps_values[0]
            q4_val = eps_values[4] if len(eps_values) >= 5 else eps_values[-1]
            growth_5q = round(((q0_val - q4_val) / abs(q4_val)) * 100, 1) if q4_val != 0 else 0

            # Database Upsert
            db_stock = db.query(models.Stock).filter(models.Stock.ticker == symbol).first()
            if not db_stock:
                db_stock = models.Stock(ticker=symbol)
                db.add(db_stock)
                
            db_stock.name = info.get('shortName', symbol)
            db_stock.sector = info.get('sector', 'N/A')
            db_stock.exchange = exchange
            db_stock.last_close = round(close_price, 2)
            db_stock.pct_off_52w_high = pct_off_52w
            db_stock.growth_5q_pct = growth_5q
            db_stock.market_cap_b = round(mcap, 2)
            db_stock.avg_vol_m = round(avg_vol, 2)
            db_stock.latest_eps_q0 = round(q0_val, 2)
            db_stock.q1_eps = round(eps_values[1], 2) if len(eps_values) > 1 else None
            db_stock.q2_eps = round(eps_values[2], 2) if len(eps_values) > 2 else None
            db_stock.q3_eps = round(eps_values[3], 2) if len(eps_values) > 3 else None
            db_stock.q4_eps = round(eps_values[4], 2) if len(eps_values) > 4 else None
            db_stock.screener_tier = tier_label
            db_stock.is_seasonal_pass = is_seasonal
            
            db.commit()
            passed_count += 1
            print(f"✓ [{tier_label}] Added {symbol} ({db_stock.name})")

        except Exception:
            continue
            
    db.close()
    print(f"Screener complete! Total matching records added: {passed_count}")

if __name__ == "__main__":
    run_screener_job()
