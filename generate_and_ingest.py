import time
import pandas as pd
import requests
from datetime import datetime

API_URL = "http://homeassistant.local:8000/api/stocks"

def generate_market_universe():
    print("Fetching active US market listings from exchange directories...")
    
    # NASDAQ Trader public symbol directories
    nasdaq_url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
    other_url = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
    
    # Read exchange files
    df_nasdaq = pd.read_csv(nasdaq_url, sep="|")
    df_nasdaq = df_nasdaq[:-1] # Drop summary row
    df_nasdaq["Market"] = "NASDAQ"
    df_nasdaq = df_nasdaq.rename(columns={"Symbol": "ticker", "Security Name": "name"})
    
    df_other = pd.read_csv(other_url, sep="|")
    df_other = df_other[:-1] # Drop summary row
    
    exchange_map = {"N": "NYSE", "A": "NYSE American", "P": "NYSE Arca"}
    df_other["Market"] = df_other["Exchange"].map(exchange_map).fillna("Other US")
    df_other = df_other.rename(columns={"ACT Symbol": "ticker", "Security Name": "name"})
    
    # Combine datasets
    df_combined = pd.concat([
        df_nasdaq[["ticker", "name", "Market"]],
        df_other[["ticker", "name", "Market"]]
    ], ignore_index=True)
    
    # Filter out test symbols containing '$'
    df_combined = df_combined[~df_combined["ticker"].str.contains(r"\$", na=False)]
    
    output_filename = "us_market_tickers.csv"
    df_combined.to_csv(output_filename, index=False)
    print(f"Successfully generated {output_filename} with {len(df_combined)} total symbols across US markets!")
    return output_filename

def run_bulk_ingestion(csv_file_path):
    df = pd.read_csv(csv_file_path)
    total = len(df)
    print(f"Starting bulk throttled ingestion for {total} stocks...")

    for idx, row in df.iterrows():
        ticker = row["ticker"]
        name = row["name"]
        market = row["Market"]
        
        # Base payload mapping to your StockCreate schema
        payload = {
            "ticker": ticker,
            "name": name,
            "sector": "General", # Categorized dynamically later
            "last_close": 0.0,
            "rsi_14": 0.0,
            "pct_off_52w_high": 0.0,
            "growth_5q_pct": 0.0,
            "market_cap_b": 0.0,
            "avg_vol_m": 0.0,
            "next_earnings": datetime.now().strftime("%Y-%m-%d"),
            "latest_eps_q0": 0.0,
            "q1_eps": 0.0,
            "q2_eps": 0.0,
            "q3_eps": 0.0,
            "q4_eps": 0.0,
            "weiss_rating": "N/A"
        }
        
        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code in [200, 201]:
                if idx % 50 == 0:
                    print(f"[{idx+1}/{total}] Synced batch up to {ticker} ({market})")
            else:
                print(f"[{idx+1}/{total}] Error for {ticker}: {response.status_code}")
        except Exception as e:
            print(f"[{idx+1}/{total}] Connection failed for {ticker}: {e}")
            time.sleep(2) # Extra pause on error
            
        # Throttling pause to protect against rate limits
        time.sleep(1.0)

if __name__ == "__main__":
    csv_file = generate_market_universe()
    run_bulk_ingestion(csv_file)
