# Threat Model — Internal Knowledge Assistant (RAG + Guardrails)

Mapped to OWASP Top 10 for LLM Applications (2025) and OWASP Top 10 for Agentic Applications (2026).

| Risk | Framework ID | Mitigation | Status |
|---|---|---|---|
| Direct prompt injection ("ignore previous instructions") | LLM01:2025 | Regex-based input classifier, blocks before retrieval | Implemented, tested |
| Indirect injection via a poisoned document | LLM01:2025 | Spotlighting: retrieved content is datamarked and explicitly framed as untrusted | Implemented, tested against a live poisoned-chunk case |
| Sensitive data disclosure across departments | LLM02:2025 | Qdrant payload filter enforces department-based RBAC at retrieval time, not in the prompt | Implemented |
| System prompt leakage | LLM07:2025 | Explicit refusal instruction; caught in eval by both input regex and output groundedness check | Implemented, tested |
| Ungrounded / hallucinated answers | LLM05:2025 | LLM-as-judge groundedness scoring before a response is returned | Implemented (moving to embedding-similarity check to reduce API cost) |
| PII leakage in responses | LLM02:2025 | Presidio scan on output, restricted to a sensitive-entity allowlist to reduce false positives | Implemented, tuned after initial false-positive finding |
| Vector store poisoning | LLM08:2025 | Source hashing at ingestion (planned) | Not yet implemented |
| Tool misuse by an agent | ASI02:2026 | Any tool/code execution routed through an isolated sandbox (Krysta/Noa) rather than executed inline | Planned |
| Unexpected code execution | ASI05:2026 | Same as above — sandbox isolation | Planned |

## Known limitations (write these up honestly — this is what a real security review looks like)
- The input-stage injection classifier is regex-based, not a trained model — it reliably catches explicit phrasing ("ignore previous instructions") but misses more subtle jailbreak framing (e.g. DAN-style prompts scored 0.4, under the 0.8 block threshold). These were still caught downstream by the output groundedness check, demonstrating the value of defense-in-depth over a single filter.
- PII detection initially over-flagged benign entities (e.g. "3 days a week" tagged as DATE_TIME), which would have blocked legitimate answers. Fixed by restricting blocking to a sensitive-entity allowlist; full entity detection is still logged for visibility.
- Groundedness scoring currently depends on an LLM-as-judge call, which is constrained by free-tier API quota — being replaced with an embedding-similarity check for cost and reliability.