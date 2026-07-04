import json
import sys
import time

def emit_event(trace_id: str, stage: str, result: dict, latency_ms: float):
    print(json.dumps({
        "trace_id": trace_id,
        "stage": stage,
        "timestamp": time.time(),
        "latency_ms": round(latency_ms, 1),
        **result,
    }), file=sys.stderr)