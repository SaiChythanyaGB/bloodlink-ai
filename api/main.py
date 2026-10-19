import os
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.db import init_db, connect
from app.seed_data import seed_demo
from app.matching import run_matching

app = FastAPI(title="BloodLink AI API", version="1.0.0", description="Educational donor-matching demo API. Synthetic data only.")
origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    init_db()
    seed_demo(False)

def rows(query, params=()):
    with connect() as c:
        return [dict(r) for r in c.execute(query, params).fetchall()]

@app.get("/")
def root():
    return {"name": "BloodLink AI API", "status": "ok", "docs": "/docs", "notice": "Educational prototype; synthetic data only."}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/overview")
def overview():
    donors = rows("SELECT * FROM donors")
    requests = rows("SELECT * FROM blood_requests")
    runs = rows("SELECT * FROM matching_runs")
    return {
        "registered_donors": len(donors),
        "available_donors": sum(1 for d in donors if d["availability_status"] == "Available"),
        "open_requests": sum(1 for r in requests if r["status"] in ("Open", "Matching in Progress")),
        "matching_runs": len(runs),
        "donors_by_blood_group": [{"blood_group": g, "count": sum(1 for d in donors if d["blood_group"] == g)} for g in ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]],
        "requests": sorted(requests, key=lambda r: r.get("created_at", ""), reverse=True)[:10],
    }

@app.get("/api/donors")
def donors():
    return rows("SELECT id, donor_code, display_name, blood_group, city_or_area, availability_status, eligibility_status FROM donors ORDER BY donor_code")

@app.get("/api/requests")
def requests():
    return rows("SELECT * FROM blood_requests WHERE status != 'Cancelled' ORDER BY created_at DESC")

class MatchInput(BaseModel):
    request_id: int
    strict_eligibility: bool = True
    require_available: bool = True
    seed: int = Field(default=7, ge=0, le=999999)

@app.post("/api/match")
def match(body: MatchInput):
    try:
        result = run_matching(body.request_id, body.strict_eligibility, body.require_available, body.seed)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Matching failed: {exc}")
