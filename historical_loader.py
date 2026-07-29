import time
from datetime import datetime
import yfinance as yf
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Stock, HistoricalPrice

def ingest_historical_dataFor_all_stocks(period="10y"):
    """
    Loops through all stocks in the database and pulls historical OHLCV data.
    """
    db: Session = SessionLocal()
    
    # Grab all ticker symbols from your database
    stocks = db.query(Stock).all()
    total_stocks = len(stocks)
    
    print(f"Found {total_stocks} stocks in database. Starting historical ingestion ({period})...")
    
    for index, stock in enumerate(stocks):
        ticker = stock.ticker
        print(f"[{index + 1}/{total_stocks}] Downloading history for {ticker}...")
        
        try:
            # Download historical data from Yahoo Finance
            tk = yf.Ticker(ticker)
            df = tk.history(period=period)
            
            if df.empty:
                print(f" -> No historical data found for {ticker}. Skipping.")
                continue
                
            # Iterate through each row of daily data
            for date_index, row in df.iterrows():
                # Extract date and clean values
                hist_date = date_index.date()
                open_p = float(row['Open']) if 'Open' in row and not pd.isna(row['Open']) else None
                high_p = float(row['High']) if 'High' in row and not pd.isna(row['High']) else None
                low_p = float(row['Low']) if 'Low' in row and not pd.isna(row['Low']) else None
                close_p = float(row['Close']) if 'Close' in row and not pd.isna(row['Close']) else None
                
                # Check for adjusted close if available, else fallback to close
                adj_close_p = float(row['Adj Close']) if 'Adj Close' in row and not pd.isna(row['Adj Close']) else close_p
                volume = int(row['Volume']) if 'Volume' in row and not pd.isna(row['Volume']) else 0
                
                if close_p is None:
                    continue

                # Check if this record already exists to prevent duplicate key errors
                existing = db.query(HistoricalPrice).filter_by(ticker=ticker, date=hist_date).first()
                
                if existing:
                    # Update existing record values
                    existing.open = open_p
                    existing.high = high_p
                    existing.low = low_p
                    existing.close_price = close_p
                    existing.adjusted_close = adj_close_p
                    existing.volume = volume
                else:
                    # Create new historical price entry
                    new_price = HistoricalPrice(
                        ticker=ticker,
                        date=hist_date,
                        open=open_p,
                        high=high_p,
                        low=low_p,
                        close_price=close_p,
                        adjusted_close=adj_close_p,
                        volume=volume
                    )
                    db.add(new_price)
            
            # Commit changes for this stock to the database
            db.commit()
            print(f" -> Successfully saved history for {ticker}.")
            
            # Brief pause to be respectful of API rate limits
            time.sleep(0.5)
            
        except Exception as e:
            db.rollback()
            print(f" -> Error processing {ticker}: {e}")
            
    db.close()
    print("Historical data ingestion complete!")

if __name__ == "__main__":
    import pandas as pd
    ingest_historical_dataFor_all_stocks(period="10y")
