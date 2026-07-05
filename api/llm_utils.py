import time
from google.genai.errors import ClientError

def call_with_retry(fn, *args, max_retries: int = 3, **kwargs):
    """Wraps any Gemini API call. On 429, waits and retries instead of crashing."""
    for attempt in range(max_retries):
        try:
            return fn(*args, **kwargs)
        except ClientError as e:
            if e.code == 429 and attempt < max_retries - 1:
                wait_s = 15  # safe default spacing for the 5 req/min free tier
                print(f"Rate limited, waiting {wait_s}s before retry ({attempt + 1}/{max_retries})...")
                time.sleep(wait_s)
            else:
                raise