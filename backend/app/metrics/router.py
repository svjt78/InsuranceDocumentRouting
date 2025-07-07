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
@cache.ttl_cache(15)  # ≤15 s staleness is fine for dashboard KPIs
def get_overview(db=Depends(get_db)):
    """
    Returns a snapshot of all dashboard KPIs:
      - status breakdown by each document status
      - daily ingestion volume
      - current backlog count
      - latency metrics (avg/p90/p99)
      - override rate (%)
      - reroute success rate (%)
    Cached for 15 seconds.
    """
    return schemas.Overview(
        status=service.status_breakdown(db),
        daily=service.daily_volume(db),
        backlog=service.backlog(db),
        latency=service.avg_latency(db),
        overrides=service.override_rate(db),
        reroute=service.reroute_success(db),
    )
