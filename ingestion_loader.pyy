import time
import random
import requests
import yfinance as yf
import pandas as pd

# Example master ticker list (expand to your full universe)
TICKERS_TO_LOAD = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META"]

def fetch_sec_edgar_fundamentals(ticker):
    """Placeholder for pulling deep historical fundamentals from SEC EDGAR."""
    headers = {'User-Agent': 'QuantEngineAdmin contact@yourdomain.com'}
    # SEC CIK lookup endpoint example
    try:
        url = f"https://data.sec.gov/submissions/CIK{ticker.zfill(10)}.json" # Simplified conceptual endpoint
        # In production, parse JSON for 10-K/10-Q metrics
        time.sleep(0.2) # Polite rate limiting for SEC guidelines (max 10 req/sec)
    except Exception as e:
        print(f"SEC EDGAR fetch warning for {ticker}: {e}")

def run_initial_ingestion():
    print("Starting rate-limited initial market data load...")
    
    for i, ticker in enumerate(TICKERS_TO_LOAD):
        success = False
        attempts = 0
        max_retries = 3
        
        while not success and attempts < max_retries:
            try:
                print(f"[{i+1}/{len(TICKERS_TO_LOAD)}] Fetching data for {ticker}...")
                
                # 1. Pull Yahoo Finance daily history
                stock = yf.Ticker(ticker)
                hist = stock.history(period="5y")
                
                if hist.empty:
                    print(f"No price history found for {ticker}.")
                    break
                
                # 2. Pull SEC Edgar fundamentals
                fetch_sec_edgar_fundamentals(ticker)
                
                # TODO: Save hist and fundamentals to your local PostgreSQL/TimescaleDB
                
                success = True
                
                # Built-in delay & jitter to prevent throttling (1.5s to 3.5s pause)
                sleep_time = random.uniform(1.5, 3.5)
                time.sleep(sleep_time)
                
            except Exception as e:
                attempts += 1
                wait_time = 2 ** attempts + random.uniform(0, 1)
                print(f"Error fetching {ticker} (Attempt {attempts}/{max_retries}): {e}. Backing off for {wait_time:.2f}s...")
                time.sleep(wait_time)
                
        if not success:
            print(f"FAILED to ingest {ticker} after max retries. Skipping to next.")

if __name__ == "__main__":
    run_initial_ingestion()
