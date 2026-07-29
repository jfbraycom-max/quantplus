from sqlalchemy.orm import Session
from app.models import Stock

def process_incoming_price(db: Session, ticker_symbol: str, incoming_price: float):
    """
    Step-by-step handler for a stock price update:
    1. Look up the stock in the database.
    2. Check if it hit a new 52-week high or low.
    3. Save changes only if a record was broken.
    """
    
    # Step 1: Find the stock in your SQLite database by its ticker symbol
    stock_record = db.query(Stock).filter(Stock.ticker == ticker_symbol.upper()).first()
    
    if not stock_record:
        print(f"Ticker {ticker_symbol} not found in database.")
        return False

    has_changed = False

    # Step 2: Check the 52-week high
    if stock_record.week_52_high is None or incoming_price > stock_record.week_52_high:
        stock_record.week_52_high = incoming_price
        has_changed = True
        print(f"-> New 52-week HIGH recorded for {ticker_symbol}: {incoming_price}")

    # Step 3: Check the 52-week low
    if stock_record.week_52_low is None or incoming_price < stock_record.week_52_low:
        stock_record.week_52_low = incoming_price
        has_changed = True
        print(f"-> New 52-week LOW recorded for {ticker_symbol}: {incoming_price}")

    # Step 4: Update the latest close price if it changed
    if stock_record.last_close != incoming_price:
        stock_record.last_close = incoming_price
        has_changed = True

    # Step 5: Save (commit) to the database ONLY if something actually changed
    if has_changed:
        db.commit()
        db.refresh(stock_record)
        print(f"Database updated successfully for {ticker_symbol}.")
    
    return has_changed
