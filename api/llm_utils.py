import time
from google.genai.errors import ClientError, ServerError

def call_with_retry(fn, *args, max_retries: int = 4, **kwargs):
    """Wraps any Gemini API call. Retries on rate limits (429) and transient
    server overload (503) instead of crashing the whole eval run."""
    for attempt in range(max_retries):
        try:
            return fn(*args, **kwargs)
        except ClientError as e:
            if e.code == 429 and attempt < max_retries - 1:
                wait_s = 15
                print(f"Rate limited (429), waiting {wait_s}s ({attempt + 1}/{max_retries})...")
                time.sleep(wait_s)
            else:
                raise
        except ServerError as e:
            if e.code == 503 and attempt < max_retries - 1:
                wait_s = 10
                print(f"Server overloaded (503), waiting {wait_s}s ({attempt + 1}/{max_retries})...")
                time.sleep(wait_s)
            else:
                raise