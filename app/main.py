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
from app.routers import learn

app = FastAPI(
    title="QuantPlus Scoring Engine API",
    description="Backend API for QuantPlus stock screening, scoring, market regimes, and watchlists.",
    version="1.0.0"
)
import os

# --- Mount Static Files & Templates ---
app.include_router(learn.router)
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
def public_landing():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Quant Earnings Pro | Advanced Quantitative Stock Screening &amp; Analysis</title>
<link rel="icon" type="image/svg+xml" href="/static/images/QpLogo.svg">
<meta name="description" content="Institutional-grade quantitative stock screening, 10-year historical market data analysis, and automated earnings insights.">
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 40px 20px; }
h1 { color: #111; font-size: 2.5rem; margin-bottom: 10px; }
.tagline { font-size: 1.25rem; color: #555; margin-bottom: 30px; }
.card { background: #f9f9f9; border: 1px solid #e5e5e5; border-radius: 8px; padding: 24px; margin-bottom: 20px; }
.btn { display: inline-block; background: #000; color: #fff; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 500; }
.btn:hover { background: #333; }

/* Glossary search widget */
.qpl-search-widget { margin-bottom: 8px; }
.qpl-search-label { font-size: 0.78rem; font-weight: 600; color: #6c63ff; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; display: block; }
.qpl-search-row { display: flex; align-items: center; background: #fff; border: 2px solid #e2e8f0; border-radius: 10px; padding: 8px 14px; transition: border-color 0.2s; gap: 8px; }
.qpl-search-row:focus-within { border-color: #6c63ff; }
.qpl-search-row svg { color: #a0aec0; flex-shrink: 0; }
.qpl-search-input { border: none; outline: none; flex: 1; font-size: 0.95rem; background: transparent; color: #1a1a2e; }
.qpl-search-input::placeholder { color: #a0aec0; }
.qpl-search-dropdown { position: absolute; top: calc(100% + 4px); left: 0; right: 0; background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.1); z-index: 100; max-height: 320px; overflow-y: auto; display: none; }
.qpl-search-wrap { position: relative; }
.qpl-result-item { padding: 10px 14px; border-bottom: 1px solid #f0f0f0; cursor: pointer; text-decoration: none; display: block; }
.qpl-result-item:hover { background: #f8f4ff; }
.qpl-result-term { font-size: 0.9rem; font-weight: 600; color: #1a1a2e; }
.qpl-result-cat { font-size: 0.75rem; color: #6c63ff; margin-top: 1px; }
.qpl-result-def { font-size: 0.78rem; color: #718096; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
.qpl-search-footer { padding: 8px 14px; text-align: center; font-size: 0.78rem; color: #6c63ff; font-weight: 600; text-decoration: none; display: block; background: #f8f4ff; border-top: 1px solid #e2e8f0; }
.qpl-search-footer:hover { background: #ede9ff; }
</style>
</head>
<body>

<img src="/static/images/QPAlogo.svg" alt="QuantPlus Analytics" style="max-width: 100%; margin-bottom: 10px;">

<!-- QuantPlus Learning Glossary Search -->
<div class="qpl-search-widget">
  <span class="qpl-search-label">&#128218; QuantPlus Learning &mdash; Financial Glossary</span>
  <div class="qpl-search-wrap">
    <div class="qpl-search-row">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input type="text" id="qplSearchInput" class="qpl-search-input"
             placeholder="Search 72 financial terms &mdash; EPS, RSI, implied volatility&hellip;"
             autocomplete="off" aria-label="Search financial glossary">
    </div>
    <div class="qpl-search-dropdown" id="qplSearchDropdown"></div>
  </div>
</div>

<img src="/static/images/QPLlogo.svg" alt="QuantPlus Learning" style="max-width: 100%; margin-bottom: 20px;">
<img src="/static/images/QEPlogo.svg" alt="Quant Earnings Pro" style="max-width: 100%; margin-bottom: 10px;">
<p class="tagline">Advanced quantitative stock analytics and data-driven market intelligence.</p>

<div class="card">
<h2>Platform Overview</h2>
<p>Quant Earnings Pro is an upcoming high-performance financial analytics engine designed to process deep historical market data, execute automated quantitative screeners, and uncover high-probability equity setups.</p>
<p>Our infrastructure tracks over a decade of granular daily stock metrics to support disciplined, systematic portfolio strategies.</p>
</div>

<div style="margin-bottom:8px;">
<h2 style="font-size:1.2rem;color:#111;margin-bottom:4px;">Featured Stock Analyses</h2>
<p style="color:#888;font-size:0.85rem;margin-top:0;">In-depth looks at companies showing sustained improvement across revenue, earnings, and earnings per share over the past five quarters. Analysis is editorial and does not constitute investment advice.</p>
</div>

<div class="card" style="border-left:4px solid #7c3aed;">
<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:12px;">
<div><span style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#7c3aed;">AI Infrastructure</span>
<h2 style="margin:4px 0 2px;">NVIDIA <span style="color:#555;font-weight:400;">(NVDA)</span></h2>
<span style="font-size:0.85rem;color:#888;">Semiconductors &nbsp;&bull;&nbsp; 5 Consecutive Improving Quarters &mdash; All Three Metrics</span></div>
<span style="background:#f5f3ff;color:#7c3aed;border:1px solid #ddd6fe;padding:4px 14px;border-radius:20px;font-size:0.8rem;font-weight:700;white-space:nowrap;">Highest EPS Growth in Universe</span></div>
<p style="color:#333;margin-bottom:10px;">NVIDIA has become the defining infrastructure company of the AI era. Its H100 and Blackwell GPU architectures are the compute substrate powering virtually every major AI model in production today &mdash; from OpenAI to Google DeepMind to thousands of enterprise deployments. Demand has outpaced supply for multiple consecutive quarters.</p>
<p style="color:#333;margin-bottom:10px;">What makes NVIDIA's position durable is not just the hardware. The CUDA software ecosystem &mdash; built over 15 years and deeply integrated into the workflows of AI researchers and engineers &mdash; creates meaningful switching costs. Competing chip manufacturers face a cold-start problem: raw performance matters less than the software tools researchers already know.</p>
<p style="color:#333;margin-bottom:16px;">Revenue, operating income, and EPS have all improved in each of the past five quarters, with EPS growth among the highest in our curated universe. The primary risks to monitor: U.S. export restrictions on advanced chips to China, and eventual normalization of data center capital expenditure cycles.</p>
<div style="background:#f5f3ff;border:1px solid #ddd6fe;border-radius:6px;padding:12px 16px;font-size:0.82rem;color:#6d28d9;"><strong>5-Quarter Growth:</strong>&nbsp; Revenue +85% &nbsp;&bull;&nbsp; Operating Income +147% &nbsp;&bull;&nbsp; EPS +215%</div>
<p style="font-size:0.75rem;color:#aaa;margin-top:14px;margin-bottom:0;">For informational purposes only. QuantPlus Analytics does not hold positions in securities discussed.</p>
</div>

<div class="card" style="border-left:4px solid #0891b2;">
<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:12px;">
<div><span style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#0891b2;">Critical Infrastructure</span>
<h2 style="margin:4px 0 2px;">Taiwan Semiconductor <span style="color:#555;font-weight:400;">(TSM)</span></h2>
<span style="font-size:0.85rem;color:#888;">Semiconductors &nbsp;&bull;&nbsp; 5 Consecutive Improving Quarters &mdash; All Three Metrics</span></div>
<span style="background:#ecfeff;color:#0891b2;border:1px solid #a5f3fc;padding:4px 14px;border-radius:20px;font-size:0.8rem;font-weight:700;white-space:nowrap;">The World&#39;s Foundry</span></div>
<p style="color:#333;margin-bottom:10px;">If NVIDIA designs the engines of the AI era, TSMC builds them. Apple, NVIDIA, AMD, Qualcomm, and Broadcom all rely on Taiwan Semiconductor to manufacture their most advanced chips. No other foundry in the world can match TSMC's process technology at leading-edge nodes &mdash; 3nm and 2nm production &mdash; making it a single point of dependency for much of the modern technology industry.</p>
<p style="color:#333;margin-bottom:10px;">That dependency cuts both ways. TSMC's competitive moat is extraordinary, but so is the geopolitical risk of a company whose primary manufacturing base sits 110 miles from mainland China. This is the single most important risk factor for any investor to understand. In direct response, TSMC is investing heavily in fab diversification &mdash; including a multi-billion dollar facility in Arizona now entering production.</p>
<p style="color:#333;margin-bottom:16px;">Financially, TSMC has delivered five consecutive quarters of improvement across all three key metrics as AI-driven semiconductor demand floods its order books. The fundamentals are hard to argue with; the geopolitical calculus is yours to weigh.</p>
<div style="background:#ecfeff;border:1px solid #a5f3fc;border-radius:6px;padding:12px 16px;font-size:0.82rem;color:#0e7490;"><strong>5-Quarter Growth:</strong>&nbsp; Revenue +36% &nbsp;&bull;&nbsp; Operating Income +65% &nbsp;&bull;&nbsp; EPS +77%</div>
<p style="font-size:0.75rem;color:#aaa;margin-top:14px;margin-bottom:0;">For informational purposes only. QuantPlus Analytics does not hold positions in securities discussed.</p>
</div>

<div class="card" style="border-left:4px solid #059669;">
<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:12px;">
<div><span style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#059669;">Consistent Compounder</span>
<h2 style="margin:4px 0 2px;">Cintas Corporation <span style="color:#555;font-weight:400;">(CTAS)</span></h2>
<span style="font-size:0.85rem;color:#888;">Business Services &nbsp;&bull;&nbsp; 5 Consecutive Improving Quarters &mdash; All Three Metrics</span></div>
<span style="background:#f0fdf4;color:#059669;border:1px solid #bbf7d0;padding:4px 14px;border-radius:20px;font-size:0.8rem;font-weight:700;white-space:nowrap;">Quiet Consistency</span></div>
<p style="color:#333;margin-bottom:10px;">Cintas doesn't make semiconductors or train AI models. It delivers uniforms, workwear, floor mats, first-aid kits, and restroom supplies to businesses across North America. It is one of the least glamorous companies you will ever research &mdash; and one of the most consistent compounders in the market.</p>
<p style="color:#333;margin-bottom:10px;">The business model is built on route density and switching costs. Once a company standardizes its workwear program with Cintas &mdash; uniforms fitted, embroidered, tracked, laundered on a weekly cycle &mdash; switching to a competitor is a genuine operational headache. That friction compounds over decades into a durable, recession-resilient revenue base that grows quietly every quarter.</p>
<p style="color:#333;margin-bottom:16px;">CTAS achieved the same five-quarter consistency score as some of the highest-growth names in our universe &mdash; not by posting explosive numbers, but by never having a bad quarter. That kind of reliability, at scale, is exactly what systematic screening is designed to surface.</p>
<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:6px;padding:12px 16px;font-size:0.82rem;color:#065f46;"><strong>5-Quarter Growth:</strong>&nbsp; Revenue +9% &nbsp;&bull;&nbsp; Operating Income +15% &nbsp;&bull;&nbsp; EPS +16% &nbsp;&bull;&nbsp; <em>Steady, not spectacular &mdash; that&#39;s the point.</em></div>
<p style="font-size:0.75rem;color:#aaa;margin-top:14px;margin-bottom:0;">For informational purposes only. QuantPlus Analytics does not hold positions in securities discussed.</p>
</div>

<div class="card" style="border-left:4px solid #2563eb;">
<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:12px;">
<div><span style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#2563eb;">Recovery Watch</span>
<h2 style="margin:4px 0 2px;">Microchip Technology <span style="color:#555;font-weight:400;">(MCHP)</span></h2>
<span style="font-size:0.85rem;color:#888;">Semiconductors &nbsp;&bull;&nbsp; 5 Consecutive Improving Quarters &mdash; Revenue &amp; Operating Income</span></div>
<span style="background:#eff6ff;color:#2563eb;border:1px solid #bfdbfe;padding:4px 14px;border-radius:20px;font-size:0.8rem;font-weight:700;white-space:nowrap;">Cyclical Turnaround</span></div>
<p style="color:#333;margin-bottom:10px;">Microchip Technology is a 30-year-old semiconductor leader &mdash; microcontrollers and analog chips for industrial, automotive, and consumer electronics. Not a new name, but one worth watching closely right now.</p>
<p style="color:#333;margin-bottom:10px;">The semiconductor sector endured one of its most severe inventory corrections in recent memory through 2024&ndash;2025. Customers who over-ordered during the COVID supply crunch spent months drawing down existing inventory rather than placing new orders. MCHP took a direct hit, posting operating losses and negative EPS through much of the cycle.</p>
<p style="color:#333;margin-bottom:10px;"><strong>What the data shows:</strong> five consecutive quarters of improving revenue (from $970M to $1.31B) and operating income (from &minus;$28.7M to $223.8M) &mdash; every major financial metric moving in the right direction, quarter after quarter.</p>
<p style="color:#333;margin-bottom:16px;font-style:italic;color:#555;"><strong>A note on our model:</strong> When a company is recovering from losses, standard percentage growth calculations produce extremely large or undefined numbers. Our screener flags these cases and excludes the distorted growth rate from composite scoring, relying instead on the consistency trend.</p>
<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:6px;padding:12px 16px;font-size:0.82rem;color:#1d4ed8;"><strong>5-Quarter Trend:</strong>&nbsp; Revenue $970M &rarr; $1.31B (+35%) &nbsp;&bull;&nbsp; Operating Income &minus;$28.7M &rarr; $223.8M &nbsp;&bull;&nbsp; EPS &minus;$0.29 &rarr; $0.21</div>
<p style="font-size:0.75rem;color:#aaa;margin-top:14px;margin-bottom:0;">For informational purposes only. QuantPlus Analytics does not hold positions in securities discussed.</p>
</div>

<div class="card" style="border-left:4px solid #d97706;">
<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:12px;">
<div><span style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#d97706;">Enterprise SaaS</span>
<h2 style="margin:4px 0 2px;">Workday <span style="color:#555;font-weight:400;">(WDAY)</span></h2>
<span style="font-size:0.85rem;color:#888;">Cloud Software &nbsp;&bull;&nbsp; Strong Operating Income &amp; Revenue Improvement</span></div>
<span style="background:#fffbeb;color:#d97706;border:1px solid #fde68a;padding:4px 14px;border-radius:20px;font-size:0.8rem;font-weight:700;white-space:nowrap;">Profitability Inflection</span></div>
<p style="color:#333;margin-bottom:10px;">Workday runs the back office of some of the world's largest organizations &mdash; HR, payroll, financial management, and workforce planning for enterprises that employ hundreds of thousands of people. It is not a flashy consumer product; it is the system a global company uses to pay its employees and close its books every quarter.</p>
<p style="color:#333;margin-bottom:10px;">That kind of software is extraordinarily sticky. When a company of 50,000 employees runs payroll on Workday, migrating to a competitor is a multi-year, nine-figure undertaking. Customer retention in enterprise HCM is among the highest in software, and Workday's annual contract values compound as customers expand usage across more modules and geographies.</p>
<p style="color:#333;margin-bottom:16px;">What the data captures is a profitability inflection. Workday spent years investing heavily in R&amp;D and sales capacity &mdash; at the expense of near-term earnings. Operating income and revenue have now improved in each of the past five quarters as that investment converts to margin expansion. EPS growth has been dramatic from a low base, reflecting the shift from a growth-at-all-costs posture to disciplined profitability.</p>
<div style="background:#fffbeb;border:1px solid #fde68a;border-radius:6px;padding:12px 16px;font-size:0.82rem;color:#92400e;"><strong>5-Quarter Growth:</strong>&nbsp; Revenue +14% &nbsp;&bull;&nbsp; Operating Income +65% &nbsp;&bull;&nbsp; EPS +248% &nbsp;&bull;&nbsp; <em>Profitability ramping as scale kicks in.</em></div>
<p style="font-size:0.75rem;color:#aaa;margin-top:14px;margin-bottom:0;">For informational purposes only. QuantPlus Analytics does not hold positions in securities discussed.</p>
</div>

<div class="card">
<h3>Member Access</h3>
<p>Authorized platform users can access the live internal testing dashboard below.</p>
<a href="/dashboard" class="btn">Private Login</a>
</div>

<script>
(function() {
  var input = document.getElementById('qplSearchInput');
  var dropdown = document.getElementById('qplSearchDropdown');
  var timer;

  input.addEventListener('input', function() {
    clearTimeout(timer);
    var q = input.value.trim();
    if (q.length < 2) { dropdown.style.display = 'none'; return; }
    timer = setTimeout(function() {
      fetch('/api/glossary/search?q=' + encodeURIComponent(q) + '&limit=6')
        .then(function(r) { return r.json(); })
        .then(function(data) {
          if (!data.length) { dropdown.style.display = 'none'; return; }
          var html = data.map(function(t) {
            return '<a class="qpl-result-item" href="/learn/glossary/' + t.slug + '">'
              + '<div class="qpl-result-term">' + t.term + '</div>'
              + '<div class="qpl-result-cat">' + t.category + '</div>'
              + '<div class="qpl-result-def">' + t.definition.slice(0, 100) + '…</div>'
              + '</a>';
          }).join('');
          html += '<a class="qpl-search-footer" href="/learn/glossary?q=' + encodeURIComponent(q) + '">Browse all 72 terms in the glossary →</a>';
          dropdown.innerHTML = html;
          dropdown.style.display = 'block';
        })
        .catch(function() { dropdown.style.display = 'none'; });
    }, 180);
  });

  document.addEventListener('click', function(e) {
    if (!e.target.closest('.qpl-search-wrap')) dropdown.style.display = 'none';
  });

  input.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
      window.location.href = '/learn/glossary?q=' + encodeURIComponent(input.value.trim());
    }
  });
})();
</script>

</body>
</html>
"""

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
<p>Welcome back, {{username}}. System operational.</p>
<div class="stats">
<h3>Database Status</h3>
<p>12,678 daily historical records loaded and indexed.</p>
</div>
</body>
</html>
"""

# --- API Status Route ---
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
    """Fetch watchlist items."""
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
