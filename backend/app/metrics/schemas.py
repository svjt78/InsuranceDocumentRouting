# app/metrics/schemas.py

from pydantic import BaseModel
from typing import List

class KV(BaseModel):
    label: str
    count: int

class DailyVolume(BaseModel):
    date: str   # ISO‐formatted date, e.g. "2025‑04‑22"
    count: int

class LatencyStats(BaseModel):
    avg: float   # average latency in seconds
    p90: float   # 90th percentile latency
    p99: float   # 99th percentile latency

class Overview(BaseModel):
    status:   List[KV]          # e.g. [{"label": "Pending", "count": 42}, …]
    daily:    List[DailyVolume] # e.g. [{"date": "2025‑04‑01", "count": 7}, …]
    backlog:  int               # pending count
    latency:  LatencyStats      # {"avg":…, "p90":…, "p99":…}
    overrides: float            # override rate percentage
    reroute:   float            # reroute success percentage
