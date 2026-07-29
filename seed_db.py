from app.database import SessionLocal
import app.models as models

db = SessionLocal()

print("Seeding initial database configuration...")

# 1. Seed Default Market Regime
if not db.query(models.MarketRegime).first():
    regime = models.MarketRegime(regime="bull", fed_rate_state="neutral", multiplier=1.0)
    db.add(regime)
    print("✓ Added default Market Regime (Bull / Neutral)")

# 2. Seed Default Strategy Score Thresholds
thresholds = [
    models.ScoreThreshold(metric_name="rsi_14", min_value=40.0, max_value=60.0, weight=0.30),
    models.ScoreThreshold(metric_name="growth_5q_pct", min_value=20.0, max_value=500.0, weight=0.40),
    models.ScoreThreshold(metric_name="market_cap_b", min_value=1.0, max_value=5000.0, weight=0.30),
]

for t in thresholds:
    if not db.query(models.ScoreThreshold).filter(models.ScoreThreshold.metric_name == t.metric_name).first():
        db.add(t)
        print(f"✓ Added threshold rule: {t.metric_name}")

# 3. Seed Sample Stock Entry (for testing UI endpoints)
if not db.query(models.Stock).filter(models.Stock.ticker == "AAPL").first():
    sample_stock = models.Stock(
        ticker="AAPL",
        name="Apple Inc.",
        sector="Technology",
        last_close=225.50,
        rsi_14=52.4,
        pct_off_52w_high=-2.1,
        growth_5q_pct=45.2,
        market_cap_b=3450.0,
        avg_vol_m=48.5,
        next_earnings="2026-08-01",
        latest_eps_q0=1.40,
        q1_eps=1.30,
        q2_eps=1.20,
        q3_eps=1.10,
        q4_eps=1.00,
        weiss_rating="A-"
    )
    db.add(sample_stock)
    print("✓ Added sample stock: AAPL")

db.commit()
db.close()
print("Database successfully populated!")
