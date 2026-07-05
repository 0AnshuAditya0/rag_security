import os
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from ..llm_utils import call_with_retry

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

nlp_config = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
}
provider = NlpEngineProvider(nlp_configuration=nlp_config)
pii_analyzer = AnalyzerEngine(nlp_engine=provider.create_engine(), supported_languages=["en"])

def check_groundedness(answer: str, context_chunks: list[str]) -> float:
    context = "\n".join(context_chunks)
    judge_prompt = f"""Context:
{context}

Answer to evaluate:
{answer}

On a scale of 0.0 to 1.0, how well is the answer supported by the context above?
Reply with ONLY a number between 0.0 and 1.0, nothing else."""

    response = call_with_retry(
        client.models.generate_content,
        model="gemini-2.5-flash-lite",
        contents=judge_prompt,
        config=types.GenerateContentConfig(temperature=0),
    )
    match = re.search(r"[01](\.\d+)?", response.text.strip())
    return float(match.group()) if match else 0.0

SENSITIVE_ENTITIES = {
    "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "US_SSN",
    "IBAN_CODE", "PERSON", "LOCATION", "US_BANK_NUMBER",
}

def check_output(answer: str, context_chunks: list[str]) -> dict:
    groundedness_score = check_groundedness(answer, context_chunks)
    pii_findings = pii_analyzer.analyze(text=answer, language="en")
    sensitive_hits = [f.entity_type for f in pii_findings if f.entity_type in SENSITIVE_ENTITIES]

    return {
        "blocked": groundedness_score < 0.5 or len(sensitive_hits) > 0,
        "groundedness_score": groundedness_score,
        "leaked_pii": sensitive_hits,
        "all_detected_entities": [f.entity_type for f in pii_findings],  # kept for debugging/eval, doesn't affect blocking
    }

if __name__ == "__main__":
    context = ["Remote work is allowed 3 days a week, subject to manager approval."]
    good_answer = "You can work from home up to 3 days a week."
    made_up_answer = "You can work from home unlimited days and get a free car."

    print("Grounded answer check:", check_output(good_answer, context))
    print("Hallucinated answer check:", check_output(made_up_answer, context))