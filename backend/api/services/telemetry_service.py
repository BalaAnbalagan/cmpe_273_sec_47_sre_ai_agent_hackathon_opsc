import time
from typing import Dict, Any
from api.services.redis_client import get_redis
from api.core.config import settings
from api.models.schemas import TelemetryEvent

# Key helpers
def k_device_zset_site(site_id: str) -> str:
    return f"devices:active:site:{site_id}"      # zset: member=device_key, score=last_seen_ts

def k_device_hash(device_key: str) -> str:
    return f"device:{device_key}"                # hash: device metadata/metrics

def device_key(site_id: str, device_type: str, device_id: str) -> str:
    return f"{site_id}|{device_type}|{device_id}"

async def ingest_telemetry(evt: TelemetryEvent) -> None:
    """
    Called by MQTT consumer worker each message.
    Stores last_seen presence in a zset and cache metrics in hash.
    """
    r = await get_redis()
    now = int(time.time())
    dkey = device_key(evt.site_id, evt.device_type, evt.device_id)

    # Update presence (zset per site)
    await r.zadd(k_device_zset_site(evt.site_id), {dkey: now})

    # Cache a small snapshot (hash)
    mapping = {
        "site_id": evt.site_id,
        "device_type": evt.device_type,
        "device_id": evt.device_id,
        "last_seen_ts": str(now),
    }
    if evt.metrics:
        # flatten a few numeric metrics; keep it small
        for mk, mv in evt.metrics.items():
            mapping[f"m:{mk}"] = str(mv)
    await r.hset(k_device_hash(dkey), mapping=mapping)

    # Optional: trim old presence beyond window
    window = settings.DEVICE_PRESENCE_WINDOW_SEC
    await r.zremrangebyscore(k_device_zset_site(evt.site_id), 0, now - window)

async def get_active_devices(site_id: str | None = None, limit: int = 20) -> Dict[str, Any]:
    """
    Returns 'active' devices within presence window (per site or all sites collected).
    For demo: fetch per-site if provided; otherwise returns {site: count, details: []} across discovered sites.
    """
    r = await get_redis()
    now = int(time.time())
    min_score = now - settings.DEVICE_PRESENCE_WINDOW_SEC

    async def site_summary(sid: str):
        # Count
        count = await r.zcount(k_device_zset_site(sid), min_score, now)
        # Top recently seen
        members = await r.zrevrangebyscore(k_device_zset_site(sid), max=now, min=min_score, start=0, num=limit)
        # Fetch hashes for details
        pipe = r.pipeline(transaction=False)
        for m in members:
            pipe.hgetall(k_device_hash(m))
        details = await pipe.execute()
        return {"site_id": sid, "active_count": count, "devices": details}

    if site_id:
        return await site_summary(site_id)

    # Discover sites (lightweight heuristic: scan for our zset key pattern)
    sites = []
    async for key in r.scan_iter(match="devices:active:site:*", count=100):
        sites.append(key.split(":")[-1])

    result = []
    total = 0
    for sid in sites:
        s = await site_summary(sid)
        total += s["active_count"]
        result.append(s)

    return {"total_active_devices": total, "sites": result}
