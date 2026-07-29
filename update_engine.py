from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Stock

def process_incoming_price(db: Session, ticker_symbol: str, incoming_price: float):
    stock_record = db.query(Stock).filter(Stock.ticker == ticker_symbol.upper()).first()
    
    if not stock_record:
        print(f"Ticker {ticker_symbol} not found in database.")
        return False

    has_changed = False

    if stock_record.week_52_high is None or incoming_price > stock_record.week_52_high:
        stock_record.week_52_high = incoming_price
        has_changed = True
        print(f"-> New 52-week HIGH recorded for {ticker_symbol}: {incoming_price}")

    if stock_record.week_52_low is None or incoming_price < stock_record.week_52_low:
        stock_record.week_52_low = incoming_price
        has_changed = True
        print(f"-> New 52-week LOW recorded for {ticker_symbol}: {incoming_price}")

    if stock_record.last_close != incoming_price:
        stock_record.last_close = incoming_price
        has_changed = True

    if has_changed:
        db.commit()
        db.refresh(stock_record)
        print(f"Database updated successfully for {ticker_symbol}.")
    
    return has_changed

# Run a quick test when executed directly
if __name__ == "__main__":
    db = SessionLocal()
    print("Testing update engine on AAPL...")
    success = process_incoming_price(db, "AAPL", 215.50)
    print("Update result:", success)
    db.close()
