# backend/app/metrics/schemas.py

from pydantic import BaseModel
from typing import List


class KV(BaseModel):
    label: str  # Document status label (e.g. "Pending", "Processed", "Failed")
    count: int  # Number of documents in this status


class DailyVolume(BaseModel):
    date: str   # ISO-formatted date, e.g. "2025-04-22"
    count: int  # Number of documents created on that date


class LatencyStats(BaseModel):
    avg: float   # Average processing latency in seconds
    p90: float   # 90th percentile latency in seconds
    p99: float   # 99th percentile latency in seconds


class Overview(BaseModel):
    status:    List[KV]          # Breakdown of documents by status
    daily:     List[DailyVolume] # Daily ingestion volumes
    backlog:   int               # Count of Pending, Failed, or No Destination documents
    latency:   LatencyStats      # Latency statistics for processed documents
    overrides: float             # Percentage of documents overridden
    reroute:   float             # Percentage of processed/No Destination docs successfully rerouted
