







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
from app.routers import learn








app = FastAPI(
    title="QuantPlus Scoring Engine API",
    description="Backend API for QuantPlus stock screening, scoring, market regimes, and watchlists.",
    version="1.0.0"
)
import os



