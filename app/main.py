from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
import app.models as models
import app.schemas as schemas

app = FastAPI(
    title="QuantPlus Scoring Engine API",
    description="Backend API for QuantPlus stock screening, scoring, market regimes, and watchlists.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"status": "QuantPlus API Online", "docs": "/docs"}

# --- Ticker & Stock Endpoints ---
@app.get("/api/stocks", response_model=List[schemas.StockResponse])
def get_stocks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Fetch all screened stocks from the database."""
    return db.query(models.Stock).offset(skip).limit(limit).all()

@app.post("/api/stocks", response_model=schemas.StockResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_stock(stock: schemas.StockCreate, db: Session = Depends(get_db)):
    """Add or update a stock record."""
    db_stock = db.query(models.Stock).filter(models.Stock.ticker == stock.ticker).first()
    if db_stock:
        for key, value in stock.model_dump().items():
            setattr(db_stock, key, value)
    else:
        db_stock = models.Stock(**stock.model_dump())
        db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

# --- Scoring Endpoints ---
@app.get("/api/scores", response_model=List[schemas.ScoreResponse])
def get_scores(ticker: str = None, limit: int = 100, db: Session = Depends(get_db)):
    """Fetch calculated scores for all tickers or a specific ticker."""
    query = db.query(models.Score)
    if ticker:
        query = query.filter(models.Score.ticker == ticker)
    return query.order_by(models.Score.created_at.desc()).limit(limit).all()

@app.post("/api/scores", response_model=schemas.ScoreResponse, status_code=status.HTTP_201_CREATED)
def create_score(score: schemas.ScoreCreate, db: Session = Depends(get_db)):
    """Record a calculated stock score."""
    db_score = models.Score(**score.model_dump())
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score

# --- Watchlist Endpoints ---
@app.get("/api/watchlists", response_model=List[schemas.WatchlistResponse])
def get_watchlist(list_type: str = None, db: Session = Depends(get_db)):
    """Fetch watchlist items (Portfolio, Almost Buy, Sell)."""
    query = db.query(models.Watchlist)
    if list_type:
        query = query.filter(models.Watchlist.list_type == list_type)
    return query.all()

@app.post("/api/watchlists", response_model=schemas.WatchlistResponse, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(item: schemas.WatchlistCreate, db: Session = Depends(get_db)):
    """Add a ticker to a watchlist."""
    db_item = models.Watchlist(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/api/watchlists/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(watchlist_id: int, db: Session = Depends(get_db)):
    """Remove an item from a watchlist by ID."""
    db_item = db.query(models.Watchlist).filter(models.Watchlist.id == watchlist_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    db.delete(db_item)
    db.commit()
    return None

# --- Score Thresholds Endpoints ---
@app.get("/api/thresholds", response_model=List[schemas.ScoreThresholdResponse])
def get_thresholds(db: Session = Depends(get_db)):
    """Fetch current scoring threshold configurations."""
    return db.query(models.ScoreThreshold).all()

@app.post("/api/thresholds", response_model=schemas.ScoreThresholdResponse, status_code=status.HTTP_201_CREATED)
def set_threshold(threshold: schemas.ScoreThresholdCreate, db: Session = Depends(get_db)):
    """Set or update a metric threshold."""
    db_t = db.query(models.ScoreThreshold).filter(models.ScoreThreshold.metric_name == threshold.metric_name).first()
    if db_t:
        db_t.min_value = threshold.min_value
        db_t.max_value = threshold.max_value
        db_t.weight = threshold.weight
    else:
        db_t = models.ScoreThreshold(**threshold.model_dump())
        db.add(db_t)
    db.commit()
    db.refresh(db_t)
    return db_t

# --- Market Regime Endpoints ---
@app.get("/api/regime", response_model=List[schemas.MarketRegimeResponse])
def get_regime(db: Session = Depends(get_db)):
    """Fetch active market regime settings."""
    return db.query(models.MarketRegime).all()

@app.post("/api/regime", response_model=schemas.MarketRegimeResponse, status_code=status.HTTP_201_CREATED)
def set_regime(regime: schemas.MarketRegimeCreate, db: Session = Depends(get_db)):
    """Set or update the active market regime."""
    db_regime = db.query(models.MarketRegime).first()
    if db_regime:
        db_regime.regime = regime.regime
        db_regime.fed_rate_state = regime.fed_rate_state
        db_regime.multiplier = regime.multiplier
    else:
        db_regime = models.MarketRegime(**regime.model_dump())
        db.add(db_regime)
    db.commit()
    db.refresh(db_regime)
    return db_regime

# --- Backtest Endpoint Stub ---
@app.post("/api/backtest", response_model=schemas.BacktestResponse)
def run_backtest_stub(request: schemas.BacktestRequest):
    """Stub endpoint for executing strategy backtests."""
    return {
        "status": "success",
        "message": f"Backtest executed from {request.start_date} to {request.end_date}",
        "parameters": request,
        "results": {
            "total_return_pct": 24.5,
            "max_drawdown_pct": -12.3,
            "sharpe_ratio": 1.85,
            "sortino_ratio": 2.15,
            "win_rate_pct": 68.4
        }
    }

# --- Trigger Screener Run Endpoint ---
from fastapi import BackgroundTasks
from app.screener import run_screener_job

@app.post("/api/run-screener")
def trigger_screener(background_tasks: BackgroundTasks, limit: int = 50):
    """Triggers the background market screener scan."""
    background_tasks.add_task(run_screener_job, limit_tickers=limit)
    return {"status": "success", "message": f"Screener background task started for top {limit} tickers."}
