from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- Stock Schemas ---
class StockBase(BaseModel):
    ticker: str
    name: Optional[str] = None
    sector: Optional[str] = None
    last_close: Optional[float] = None
    rsi_14: Optional[float] = None
    pct_off_52w_high: Optional[float] = None
    growth_5q_pct: Optional[float] = None
    market_cap_b: Optional[float] = None
    avg_vol_m: Optional[float] = None
    next_earnings: Optional[str] = None
    latest_eps_q0: Optional[float] = None
    q1_eps: Optional[float] = None
    q2_eps: Optional[float] = None
    q3_eps: Optional[float] = None
    q4_eps: Optional[float] = None
    weiss_rating: Optional[str] = "N/A"

class StockCreate(StockBase):
    pass

class StockResponse(StockBase):
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Score Schemas ---
class ScoreBase(BaseModel):
    ticker: str
    mode: str
    fundamental_score: float
    technical_score: float
    news_score: float
    final_score: float

class ScoreCreate(ScoreBase):
    pass

class ScoreResponse(ScoreBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Score Threshold Schemas ---
class ScoreThresholdBase(BaseModel):
    metric_name: str
    min_value: float
    max_value: float
    weight: float

class ScoreThresholdCreate(ScoreThresholdBase):
    pass

class ScoreThresholdResponse(ScoreThresholdBase):
    id: int

    class Config:
        from_attributes = True

# --- Market Regime Schemas ---
class MarketRegimeBase(BaseModel):
    regime: str
    fed_rate_state: str
    multiplier: float = 1.0

class MarketRegimeCreate(MarketRegimeBase):
    pass

class MarketRegimeResponse(MarketRegimeBase):
    id: int
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Watchlist Schemas ---
class WatchlistBase(BaseModel):
    ticker: str
    list_type: str
    target_price: Optional[float] = None

class WatchlistCreate(WatchlistBase):
    pass

class WatchlistResponse(WatchlistBase):
    id: int
    added_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Backtest Stub Schemas ---
class BacktestRequest(BaseModel):
    start_date: str
    end_date: str
    initial_capital: float = 10000.0
    mode: str = "Mode A"

class BacktestResponse(BaseModel):
    status: str
    message: str
    parameters: BacktestRequest
    results: dict
