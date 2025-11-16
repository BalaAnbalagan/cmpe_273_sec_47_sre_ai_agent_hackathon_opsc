import time
from typing import Dict, Any
from backend.api.services.redis_client import get_redis
from backend.api.core.config import settings
from backend.api.models.schemas import UserMetric

def k_user_zset_site(site_id: str) -> str:
    return f"users:active:site:{site_id}"        # zset: member=session_id, score=last_seen

def k_user_hash(session_id: str) -> str:
    return f"user:session:{session_id}"          # hash: small snapshot

def k_user_metrics_site(site_id: str) -> str:
    return f"users:metrics:site:{site_id}"       # hash: cpu/latency/mem aggregates (last)

async def ingest_user_metric(m: UserMetric) -> None:
    r = await get_redis()
    now = int(time.time())

    # mark presence
    await r.zadd(k_user_zset_site(m.site_id), {m.session_id: now})

    # small session snapshot
    mapping = {
        "session_id": m.session_id,
        "site_id": m.site_id,
        "user_id": m.user_id,
        "last_seen_ts": str(now),
    }
    if m.latency_ms is not None: mapping["latency_ms"] = str(m.latency_ms)
    if m.cpu_pct    is not None: mapping["cpu_pct"]    = str(m.cpu_pct)
    if m.mem_pct    is not None: mapping["mem_pct"]    = str(m.mem_pct)

    await r.hset(k_user_hash(m.session_id), mapping=mapping)

    # keep last metrics per site (you can evolve this to percentiles)
    latest = {}
    if m.latency_ms is not None: latest["latency_ms_last"] = str(m.latency_ms)
    if m.cpu_pct    is not None: latest["cpu_pct_last"]    = str(m.cpu_pct)
    if m.mem_pct    is not None: latest["mem_pct_last"]    = str(m.mem_pct)
    if latest:
        await r.hset(k_user_metrics_site(m.site_id), mapping=latest)

    # trim presence window
    window = settings.USER_PRESENCE_WINDOW_SEC
    await r.zremrangebyscore(k_user_zset_site(m.site_id), 0, now - window)

async def get_active_users(site_id: str, limit: int = 50) -> Dict[str, Any]:
    r = await get_redis()
    now = int(time.time())
    min_score = now - settings.USER_PRESENCE_WINDOW_SEC

    count = await r.zcount(k_user_zset_site(site_id), min_score, now)
    sessions = await r.zrevrangebyscore(k_user_zset_site(site_id), max=now, min=min_score, start=0, num=limit)

    pipe = r.pipeline(transaction=False)
    for s in sessions:
        pipe.hgetall(k_user_hash(s))
    session_details = await pipe.execute()

    metrics = await r.hgetall(k_user_metrics_site(site_id))
    return {
        "site_id": site_id,
        "active_user_count": count,
        "sessions": session_details,
        "latest_site_metrics": metrics,
        "window_sec": settings.USER_PRESENCE_WINDOW_SEC
    }
