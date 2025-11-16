import re
from typing import List, Tuple
from api.services.redis_client import get_redis

# Simple regex for common web logs: 'IP - - [ts] "GET /..." status bytes ...'
LOG_RE = re.compile(r'(?P<ip>\d{1,3}(?:\.\d{1,3}){3}).*?"\w+ [^"]+" (?P<status>\d{3})')

def k_errors_by_ip(status: str) -> str:
    return f"logs:status:{status}:by_ip"   # hash: {ip -> count}

async def ingest_log_line(line: str) -> None:
    r = await get_redis()
    m = LOG_RE.search(line)
    if not m:
        return
    ip = m.group("ip")
    status = m.group("status")
    await r.hincrby(k_errors_by_ip(status), ip, 1)

async def top_error_ips(status: str = "400", top_n: int = 10) -> List[Tuple[str, int]]:
    r = await get_redis()
    raw = await r.hgetall(k_errors_by_ip(status))
    pairs = [(ip, int(cnt)) for ip, cnt in raw.items()]
    pairs.sort(key=lambda x: x[1], reverse=True)
    return pairs[:top_n]
