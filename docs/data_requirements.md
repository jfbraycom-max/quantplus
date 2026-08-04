QuantPlus Data Requirements & Roadmap
Executive Summary
You already have 10 years of company financials and 10 years of daily closes for U.S. equities. That's a strong foundation for fundamentals-driven signals and long-term backtests, but it's insufficient for the earnings-and-options features we prioritized (IV Squeeze, option prediction models, flow signals, backtesting realistic options strategies, real-time alerts).

Below is an exact list of datasets needed, why each is required, frequency/retention/quality expectations, schema/fields to collect, estimated volumes, priority (mapped to roadmap phases), gaps vs what is already in hand, and recommended next steps.


1. High-Level Data Inventory
A. Options Market Data (core requirement)
Why: All options features (IV surface, squeeze detection, strategy payoffs, backtesting, flow signals) require full options chain history and snapshots.

Datasets:

Options chain snapshots (per timestamp) — full chain across strikes & expiries
Historical options trades / consolidated options tape (prints) — for flow/unusual activity
Open interest (OI) history — per strike/expiry over time
Implied volatility (IV) per option — if vendor provides; otherwise compute from mid prices
Greeks (delta, gamma, vega, theta) — per option (or compute)
Bid/ask sizes and exchange flags — for liquidity and trade classification
Options-level historical mid/ask/bid time series — for backtesting fills

Frequency:

Real-time / tick for flow and premium tiers
Intraday snapshots (e.g., 1s–1m) for high-quality backtests and IV surface evolution
Daily end-of-day for lower tiers

Retention: Full tick/intraday for at least 2 years for high-value tickers; 5–10 years of EOD and hourly surfaces for historical research.

Key fields (canonical):

timestamp, symbol, underlying_price, strike, expiry_date, option_type (C/P),

bid, ask, last, mid, bid_size, ask_size, volume, open_interest,

implied_vol, delta, gamma, vega, theta, exchange, trade_flag,

print_size, print_price

Gap vs current: No options data yet. This is the largest gap. Priority: Phase A/B (IV Squeeze, Alerts, Prediction Model, Backtesting)


B. Underlying Price Data (enhanced)
Why: Daily closes are good for long-term studies, but options work needs intraday underlying prices and tick data for accurate P&L, fills, and IV recomputation.

Datasets:

Intraday trade ticks (best) or 1s/1m bars for underlying
NBBO / Level 1 quotes (bid/ask) for accurate mid price and slippage modeling
Corporate actions: splits, dividends, delistings, symbol changes

Frequency & retention: Tick/1s/1m for last 2–3 years for top tickers; 1m/5m for longer history. Keep corporate actions indefinitely.

Key fields:

timestamp, symbol, price, size, bid, ask, exchange,

trade_condition, split_factor, dividend_amount

Gap vs current: Daily closes only; need intraday/tick for realistic options backtests and IV surface dynamics. Priority: Phase A/B


C. Earnings & Estimates Data (canonical event data)
Why: Core to everything — event dates, consensus estimates, historical surprises, and timestamps for pre/post windows.

Datasets:

Canonical earnings calendar (actual release timestamp, not just date)
Consensus EPS & revenue estimates (per quarter), analyst coverage metadata
Historical reported EPS/revenue and surprise (reported − consensus)
Guidance and conference call transcripts (optional for advanced models)

Frequency: Update daily; store historical per-quarter values.

Key fields:

symbol, earnings_datetime (timestamp), period_end,

consensus_eps, consensus_rev, reported_eps, reported_rev,

surprise_pct, source

Gap vs current: Likely have earnings dates in financials but may lack exact timestamps and consensus estimates. Confirm. Priority: Phase A (calendar + predicted move)


D. Analyst & Market Sentiment Data
Why: Sentiment and news flow can be predictive for direction and for modeling informed flow.

Datasets:

News headlines & article metadata (timestamped)
Social sentiment (Twitter/Reddit aggregated scores)
Analyst upgrades/downgrades and target price changes

Frequency: Real-time ingestion for alerts; historical archive for model features.

Key fields:

timestamp, symbol, source, headline, sentiment_score, article_text_id

Gap vs current: Likely missing. Priority: Phase B (model features)


E. Options Flow / Trade Tape (real-time)
Why: To detect unusual sweeps, block trades, and directional intent.

Datasets:

Consolidated options prints with flags (sweep, block, opening/closing)
Large trade aggregation (size thresholds)
Exchange-level flags

Frequency: Tick; low-latency (<1s) for premium tiers.

Key fields:

timestamp, symbol, strike, expiry, option_type,

trade_price, trade_size, exchange, flags, buyer_initiated

Gap vs current: Missing. Priority: Phase C (enterprise, flow signals)


F. Market & Macro Data
Why: VIX term structure, interest rates, FX, and macro volatility influence IV and hedging.

Datasets:

VIX index and VIX futures term structure
Interest rates (Treasury yields)
Macro volatility indices (e.g., MOVE for rates)
Sector/ETF prices & options

Frequency: Intraday for VIX; daily for rates.

Key fields:

timestamp, ticker, price, expiry (for futures), implied_vol

Gap vs current: Likely partial; may have daily closes for ETFs but need VIX term structure. Priority: Phase B/C


G. Corporate Ownership, Short Interest & Institutional Flows
Why: Short interest and institutional positioning can amplify earnings moves and options flow interpretation.

Datasets:

Short interest (biweekly)
13F holdings (quarterly)
Insider trades (SEC filings)
Institutional ownership changes

Priority: Phase B


H. Brokerage/Execution & Margin Rules (for realistic P&L)
Why: To compute margin, commissions, assignment risk, and realistic fills.

Datasets:

Broker margin rules per account type
Commission schedules
Assignment/early exercise probabilities (model or historical)

Priority: Phase B/C (backtesting realism, risk dashboard)


2. Canonical Schemas
Options Snapshot (row per option quote)
Field
Type
Notes
timestamp
ISO8601


underlying_symbol
string


option_symbol
string
Standardized (OCC format)
strike
float


expiry_date
YYYY-MM-DD


option_type
C/P


bid
float


ask
float


mid
float
(bid+ask)/2 if missing
bid_size
int


ask_size
int


last
float


volume
int


open_interest
int
Non-negative
implied_vol
float
[0, 5] bounds
delta
float


gamma
float


vega
float


theta
float


exchange
string


source
string
Vendor ID
ingest_ts
timestamp
System timestamp

Options Trade Print
timestamp, option_symbol, trade_price, trade_size,

buyer_initiated (bool), exchange, flags, print_id, source
Underlying Tick
timestamp, symbol, price, size, bid, ask, exchange, trade_condition
Earnings Event
symbol, earnings_timestamp, period_end,

consensus_eps, consensus_rev, reported_eps, reported_rev,

surprise_pct, source
Validation Rules
No null: timestamp, option_symbol, strike, expiry
bid <= ask; mid = (bid+ask)/2 if missing
implied_vol within [0, 5]
open_interest non-negative integer


3. Estimated Data Volumes & Storage
Assume universe = 3,000 liquid tickers for premium real-time tier.

Data Type
Cadence
Recommendation
Options snapshots
1s
Top 200 tickers at 1s; top 1,000 at 1m; EOD for rest
Options trade prints
Tick
Millions of prints/day across universe
Underlying bars
1m
Top 1,000 tickers


Storage architecture:

Hot store (last 30 days): ClickHouse / kdb / Timescale for real-time queries and alerts
Cold store: S3 Parquet partitioned by date/symbol/expiry
Metadata DB: Postgres for catalog, ingestion status, vendor metadata


4. Vendor Shortlist
Data Type
Vendors
Options chains & historical
CBOE LiveVol, OptionMetrics (IvyDB), TickData, QuantHouse, Tradier, Interactive Brokers
Options flow / trade tape
OPRA feeds, LiveVol, Trade Alert, CheddarFlow
Intraday underlying ticks
NYSE/NASDAQ TAQ, Polygon.io, IEX, QuantQuote
Earnings & estimates
Refinitiv, FactSet, Zacks, Estimize, I/B/E/S
News & sentiment
RavenPack, Bloomberg, LexisNexis, NewsAPI, StockTwits
Short interest / ownership
S3 filings, Quandl, Refinitiv


Key tradeoff: Real-time tape is expensive. Consider tiered access — EOD for most users, real-time for enterprise.


5. Current Data Gaps Summary
Dataset
Have
Need
10yr company financials
✅
—
10yr daily closes
✅
—
Options chain history & snapshots
❌
Critical
Options trade prints / flow
❌
Critical
Intraday underlying (tick/1m)
❌
Critical
Consensus estimates + exact earnings timestamps
❓
Confirm
VIX term structure
❌
Phase B
News / sentiment feeds
❌
Phase B
Margin rules & commission schedules
❌
Phase B/C



6. Data Engineering & ETL Requirements
Ingestion pipeline:

Modular per vendor with schema mapping and validation
Normalize option symbols to OCC standard
Compute on ingest: mid, implied_vol, moneyness, days_to_expiry, IV_percentile (rolling), IV_rank

Reconciliation:

Daily jobs: compare EOD aggregated volume/OI vs vendor reports; alert on >1–2% mismatch
Data quality dashboards: null rates, latency percentiles, missing expiries

Feature pipelines (nightly):

IV term structure, skew metrics, squeeze score
Historical surprise distributions
Precomputed surfaces for top N tickers


7. Model & Backtest Implications
Feature
Data Required
IV Squeeze detector
Historical IV surfaces (daily/hourly) + realized vol; IV percentile + compression metrics
Option prediction model
Pre-event IV term structure, skew, flow features (24–72h window), fundamentals, sentiment, historical surprise distribution
Backtesting engine
Minute/tick options & underlying for fills, early exercise, assignment, IV crush simulation
Explainability
Feature attributions per prediction must be stored with feature values



8. Phased Data Acquisition Plan
Phase A — Fastest Path to Value
Acquire EOD options chains + daily IV surfaces for top 1,000 tickers
Acquire earnings consensus + exact timestamps
Ingest 1m underlying bars for top tickers
Build nightly feature pipelines and IV Squeeze detector
Phase B — Model & Strategy
Add intraday options snapshots (1m or 1s for top 200) + trade prints
Add news/sentiment and VIX term structure
Build prediction model and scenario simulator
Phase C — Real-Time & Enterprise
Full tick-level options trade tape + 1s snapshots for top N
Streaming APIs and webhooks
Risk dashboard


9. Quality & Acceptance Metrics
Metric
Target
Options chain completeness (strikes/expiries present)
>99% for top tickers
Ingest latency (95th percentile)
<1s for premium
Mid price accuracy vs vendor
<0.1% average difference
Daily volume/OI reconciliation mismatch
<1–2%
Model feature null rate
<0.5%



10. Immediate Next Steps
Confirm what is already in the DB beyond financials & daily closes — earnings consensus? exact timestamps? corporate actions? intraday ticks?
Procure EOD options chains + daily IV surfaces for top 1,000 tickers (fastest path to IV Squeeze)
Define canonical schemas and ingestion contracts for options snapshots and prints
Run pilot ingestion: 50 tickers, 1m options snapshots + 1m underlying bars + earnings calendar — validate storage, compute, and IV computation
Build nightly feature pipeline: IV percentiles, squeeze score, historical surfaces for top tickers
Run retrospective analysis: compute IV Squeeze signals on historical data and measure post-event moves to set thresholds
Begin vendor evaluation for trade tape and real-time prints (long procurement lead time)


11. Deliverables Available
Upon request, the following repo-ready artifacts can be produced:

Data Inventory CSV — each dataset, required fields, frequency, retention, priority, vendor candidates
Canonical JSON schemas — options snapshot, trade print, underlying tick, earnings event
ETL template (Python) — ingest vendor CSV/JSON into Parquet, compute IV/mid
Pilot plan — step-by-step to ingest 50 tickers for 90 days of intraday data
Vendor shortlist & cost estimate (ballpark) — options chains, trade tape, news/sentiment

