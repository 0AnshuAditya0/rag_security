import json
import sys
import time
import os
import redis

_redis = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"))
KEY_PREFIX = "rag_sec:"  # namespaced so this never collides with Noa's keys on the shared Redis

def emit_event(trace_id: str, stage: str, result: dict, latency_ms: float):
    event = {
        "trace_id": trace_id,
        "stage": stage,
        "timestamp": time.time(),
        "latency_ms": round(latency_ms, 1),
        **result,
    }
    print(json.dumps(event), file=sys.stderr)

    # Push to a capped list (keep last 500 events) and bump simple counters
    _redis.lpush(f"{KEY_PREFIX}events", json.dumps(event))
    _redis.ltrim(f"{KEY_PREFIX}events", 0, 499)

    if result.get("blocked"):
        _redis.incr(f"{KEY_PREFIX}blocked:{stage}")
    _redis.incr(f"{KEY_PREFIX}total:{stage}")

def get_stats() -> dict:
    stages = ["input_guardrail", "output_guardrail"]
    stats = {}
    for stage in stages:
        total = int(_redis.get(f"{KEY_PREFIX}total:{stage}") or 0)
        blocked = int(_redis.get(f"{KEY_PREFIX}blocked:{stage}") or 0)
        stats[stage] = {"total": total, "blocked": blocked}

    recent_raw = _redis.lrange(f"{KEY_PREFIX}events", 0, 19)  # last 20 events
    stats["recent_events"] = [json.loads(e) for e in recent_raw]
    return stats