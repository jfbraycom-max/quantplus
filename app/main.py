
from sqlalchemy.orm import Session
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import secrets

from app.database import get_db
import app.models as models
import app.schemas as schemas

app = FastAPI(
    title="QuantPlus Scoring Engine API",
    description="Backend API for QuantPlus stock screening, scoring, market regimes, and watchlists.",
    version="1.0.0"
)

# --- Mount Static Files & Templates ---
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="templates")

security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_user = secrets.compare_digest(credentials.username, "admin")
    correct_pass = secrets.compare_digest(credentials.password, "your_secure_password")
    if not (correct_user and correct_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# --- PUBLIC SEO LANDING PAGE ---

@app.get("/", response_class=HTMLResponse)
def public_landing(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- PRIVATE SECURE DASHBOARD ---
@app.get("/dashboard", response_class=HTMLResponse)
def private_dashboard(username: str = Depends(verify_admin)):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Quant Earnings Pro - Internal Dashboard</title>
        <style>
            body {{ font-family: sans-serif; padding: 40px; background: #121212; color: #e0e0e0; }}
            .stats {{ background: #1e1e1e; padding: 20px; border-radius: 8px; border: 1px solid #333; }}
        </style>
    </head>
    <body>
        <h1>Internal Analytics Dashboard</h1>
        <p>Welcome back, {username}. System operational.</p>
        <div class="stats">
            <h3>Database Status</h3>
            <p>12,678 daily historical records loaded and indexed.</p>
        </div>
    </body>
    </html>
    """

# --- API Status Route (Previous Root) ---
@app.get("/api/status")
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
