from fastapi import APIRouter, Depends
from ..database import SessionLocal
from . import service, schemas, cache
from sqlalchemy.sql import text

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


@router.get("/debug")
def debug_metrics(db=Depends(get_db)):
    """Debug endpoint to check what data exists"""
    # Check August 2025 data specifically
    august_data = db.execute(text("""
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as count
        FROM documents1 
        WHERE created_at >= '2025-08-01' AND created_at < '2025-09-01'
        GROUP BY DATE(created_at)
        ORDER BY date
    """)).all()
    
    # Check what the daily_volume service returns
    daily_volume_data = service.daily_volume(db)
    
    # Check recent documents
    recent_docs = db.execute(text("""
        SELECT id, filename, created_at, DATE(created_at) as date
        FROM documents1 
        ORDER BY created_at DESC 
        LIMIT 5
    """)).all()
    
    return {
        "august_2025_data": [
            {"date": str(row.date), "count": row.count} 
            for row in august_data
        ],
        "service_daily_volume": daily_volume_data,
        "recent_documents": [
            {
                "id": row.id,
                "filename": row.filename, 
                "created_at": str(row.created_at),
                "date": str(row.date)
            }
            for row in recent_docs
        ],
        "comparison": {
            "august_count": len(august_data),
            "service_count": len(daily_volume_data)
        }
    }


@router.get("/fresh", response_model=schemas.Overview)
def get_fresh_overview(db=Depends(get_db)):
    """Returns non-cached metrics for comparison"""
    return schemas.Overview(
        status=service.status_breakdown(db),
        daily=service.daily_volume(db),
        backlog=service.backlog(db),
        latency=service.avg_latency(db),
        overrides=service.override_rate(db),
        reroute=service.reroute_success(db),
    )
