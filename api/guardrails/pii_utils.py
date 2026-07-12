import re

PII_PATTERNS = {
    "EMAIL_ADDRESS": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "PHONE_NUMBER": r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
    "US_SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "IBAN_CODE": r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b",
}

def detect_pii(text: str) -> list[str]:
    found = []
    for entity_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, text):
            found.append(entity_type)
    return found