
import os
from collections import defaultdict

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.environ.get("ANALYTICS_API_KEY", "")

class Event(BaseModel):
    user: str
    amount: float
    ts: int

class EventBatch(BaseModel):
    events: list[Event]

@app.post("/analytics")
def analytics(
    batch: EventBatch,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    if not API_KEY or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    events = batch.events
    totals = defaultdict(float)

    for event in events:
        if event.amount > 0:
            totals[event.user] += event.amount

    top_user = max(totals, key=totals.get) if totals else ""

    return {
        "email": os.environ.get("STUDENT_EMAIL", "24f2000638@ds.study.iitm.ac.in"),
        "total_events": len(events),
        "unique_users": len({event.user for event in events}),
        "revenue": sum(e.amount for e in events if e.amount > 0),
        "top_user": top_user,
    }

@app.get("/")
def root():
    return {"status": "ok"}

