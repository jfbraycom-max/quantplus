from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Stock(Base):
    __tablename__ = "stocks"

    ticker = Column(String, primary_key=True, index=True)
    name = Column(String)
    sector = Column(String)
    last_close = Column(Float)
    rsi_14 = Column(Float)
    pct_off_52w_high = Column(Float)
    growth_5q_pct = Column(Float)
    market_cap_b = Column(Float)
    avg_vol_m = Column(Float)
    next_earnings = Column(String)
    
    latest_eps_q0 = Column(Float)
    q1_eps = Column(Float)
    q2_eps = Column(Float)
    q3_eps = Column(Float)
    q4_eps = Column(Float)
    week_52_high = Column(Float, nullable=True)
    week_52_high_date = Column(Date, nullable=True)
    week_52_low = Column(Float, nullable=True)
    week_52_low_date = Column(Date, nullable=True) 
    
    weiss_rating = Column(String, default="N/A")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, ForeignKey("stocks.ticker"), index=True)
    mode = Column(String)
    fundamental_score = Column(Float)
    technical_score = Column(Float)
    news_score = Column(Float)
    final_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ScoreThreshold(Base):
    __tablename__ = "score_thresholds"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, unique=True, index=True)
    min_value = Column(Float)
    max_value = Column(Float)
    weight = Column(Float)


class MarketRegime(Base):
    __tablename__ = "market_regimes"

    id = Column(Integer, primary_key=True, index=True)
    regime = Column(String)
    fed_rate_state = Column(String)
    multiplier = Column(Float, default=1.0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, ForeignKey("stocks.ticker"), index=True)
    list_type = Column(String, index=True)
    target_price = Column(Float, nullable=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now())


from sqlalchemy import Index, Date

class HistoricalPrice(Base):
    __tablename__ = "historical_prices"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, ForeignKey("stocks.ticker"), index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close_price = Column(Float, nullable=False)
    adjusted_close = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)

    __table_args__ = (
        Index('idx_ticker_date', "ticker", "date", unique=True),
    )


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    subscription_tier = Column(String, default="Free") # Free, Pro, Enterprise
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TieredWatchlist(Base):
    __tablename__ = "tiered_watchlists"

    id = Column(Integer, primary_key=True, index=True)
    tier_level = Column(String, index=True, nullable=False) # Free, Pro, Enterprise
    ticker = Column(String, ForeignKey("stocks.ticker"), index=True, nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
