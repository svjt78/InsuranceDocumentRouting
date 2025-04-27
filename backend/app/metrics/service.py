# backend/app/metrics/service.py

from sqlalchemy.sql import text

def status_breakdown(db):
    """
    Returns a list of { label, count } dicts summarizing document counts by status.
    """
    sql = text("""
        SELECT status, COUNT(*) AS cnt
        FROM documents
        GROUP BY status;
    """)
    return [
        {"label": row.status, "count": row.cnt}
        for row in db.execute(sql)
    ]


def daily_volume(db):
    """
    Returns a list of { date, count } dicts for each day
    on which documents were created.
    """
    sql = text("""
        SELECT
            DATE(created_at) AS date,
            COUNT(*)         AS count
        FROM documents
        GROUP BY DATE(created_at)
        ORDER BY DATE(created_at);
    """)
    return [
        {"date": row.date.isoformat(), "count": row.count}
        for row in db.execute(sql)
    ]


def backlog(db):
    """
    Returns the total number of documents with status Pending, failed, or No Destination.
    """
    sql = text("""
        SELECT COUNT(*) AS cnt
        FROM documents
        WHERE status IN ('Pending', 'failed', 'No Destination');
    """)
    return db.execute(sql).scalar_one()


def avg_latency(db):
    """
    Returns average and percentile latencies (in seconds), for docs
    whose status is exactly 'Processed'. Results are rounded to one decimal.
    """
    sql = text("""
      SELECT
        AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) AS avg,
        PERCENTILE_CONT(0.90) WITHIN GROUP (
          ORDER BY EXTRACT(EPOCH FROM (updated_at - created_at))
        ) AS p90,
        PERCENTILE_CONT(0.99) WITHIN GROUP (
          ORDER BY EXTRACT(EPOCH FROM (updated_at - created_at))
        ) AS p99
      FROM documents
      WHERE status = 'Processed'
        AND updated_at IS NOT NULL;
    """)
    row = db.execute(sql).one()
    return {
        "avg":  round(row.avg,  1) if row.avg  is not None else 0.0,
        "p90": round(row.p90, 1) if row.p90 is not None else 0.0,
        "p99": round(row.p99, 1) if row.p99 is not None else 0.0,
    }


def override_rate(db):
    """
    Returns the percentage of documents overridden, including
    both 'Overridden%' statuses and 'Processed with Override'.
    """
    sql = text("""
        WITH total AS (
          SELECT COUNT(*) AS t FROM documents
        ), over AS (
          SELECT COUNT(*) AS o
          FROM documents
          WHERE status LIKE 'Overridden%' OR status = 'Processed with Override'
        )
        SELECT (o::float / t) * 100.0 AS pct
        FROM total, over;
    """)
    return db.execute(sql).scalar_one()


def reroute_success(db):
    """
    Returns the percentage of documents with non-null destination_bucket
    among those whose status is either like 'Processed%' or exactly 'No Destination'.
    """
    sql = text("""
        WITH total AS (
          SELECT COUNT(*) AS t
          FROM documents
          WHERE status LIKE 'Processed%' OR status = 'No Destination'
        ), rerouted AS (
          SELECT COUNT(*) AS r
          FROM documents
          WHERE (status LIKE 'Processed%' OR status = 'No Destination')
            AND destination_bucket IS NOT NULL
        )
        SELECT (r::float / t) * 100.0 AS pct
        FROM total, rerouted;
    """)
    return db.execute(sql).scalar_one()