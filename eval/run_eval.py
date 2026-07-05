import json
from api.orchestrator import run_pipeline
import time

def run_eval(test_file: str):
    results = {
        "malicious_total": 0, "malicious_blocked": 0,
        "benign_total": 0, "benign_blocked": 0,
    }
    details = []

    with open(test_file) as f:
        for line in f:
            case = json.loads(line.strip())
            outcome = run_pipeline(case["prompt"])
            was_blocked = outcome["blocked_at"] is not None

            if case["label"] == "malicious":
                results["malicious_total"] += 1
                results["malicious_blocked"] += was_blocked
            else:
                results["benign_total"] += 1
                results["benign_blocked"] += was_blocked

            details.append({"prompt": case["prompt"], "label": case["label"], "blocked": was_blocked, "blocked_at": outcome["blocked_at"]})
            time.sleep(15)
            
    attack_detection_rate = results["malicious_blocked"] / results["malicious_total"] if results["malicious_total"] else 0
    false_positive_rate = results["benign_blocked"] / results["benign_total"] if results["benign_total"] else 0

    print(f"Attack detection rate: {attack_detection_rate:.0%} ({results['malicious_blocked']}/{results['malicious_total']})")
    print(f"False positive rate: {false_positive_rate:.0%} ({results['benign_blocked']}/{results['benign_total']})")
    print()
    for d in details:
        status = "BLOCKED" if d["blocked"] else "passed"
        print(f"[{d['label']:>9}] {status:>7} ({d['blocked_at']}) — {d['prompt'][:60]}")

if __name__ == "__main__":
    run_eval("eval/adversarial_prompts.jsonl")