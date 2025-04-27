# backend/app/metrics/router.py
from fastapi import APIRouter, Depends
from ..database import SessionLocal
from . import service, schemas, cache

router = APIRouter(prefix="/metrics", tags=["Metrics"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/overview", response_model=schemas.Overview)
@cache.ttl_cache(15)  # ≤15 s staleness is fine for a dashboard
def get_overview(db=Depends(get_db)):
    """
    Returns a snapshot of all dashboard KPIs, cached for 15 seconds.
    """
    return schemas.Overview(
        status=service.status_breakdown(db),
        daily=service.daily_volume(db),
        backlog=service.backlog(db),
        latency=service.avg_latency(db),
        overrides=service.override_rate(db),
        reroute=service.reroute_success(db),
    )
