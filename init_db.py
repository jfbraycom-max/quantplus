from app.database import engine, Base
import app.models

print("Creating database tables in data/quantplus.db...")
Base.metadata.create_all(bind=engine)
print("Database schema successfully created!")
