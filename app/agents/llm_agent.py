
import json

from groq import Groq
from app.core.config import settings


def generate_explanation(
    facts,
    previous_response=None,
    mismatches=None
):
    client = Groq(api_key=settings.groq_api_key)

    correction = ""

    if previous_response:
        correction = f"""
Your previous explanation contained factual mismatches.

Previous explanation:
{previous_response}

Mismatches identified by the Python validator:
{json.dumps(mismatches, ensure_ascii=False)}

Generate a corrected explanation.

Use ONLY the verified facts provided below.
Correct every identified mismatch.
"""

    system_prompt = """
You are a financial crime investigation explanation agent.

The deterministic Python detector is the ONLY source of truth.

STRICT RULES:

1. Use only the supplied verified facts.
2. Never change factual values.
3. Never invent transaction information.
4. Never independently make flagging decisions.
5. Never claim that financial crime has occurred.
6. Do not omit any required factual field.
7. Use numerical digits, not number words.
8. Use ₹ for monetary values.
9. Do not include additional numerical claims.

Return valid JSON with EXACTLY ONE key:

{
    "explanation": "string"
}

The explanation MUST follow this exact structure:

Account ID: <account_id>

Transaction Count: <transaction_count> transactions

Total Amount: ₹<total_amount>

Threshold: ₹<threshold>

Time Window: <window_hours> hours

Investigation Explanation:
Write a short explanation of the detected transaction pattern.

Investigation Result:
Explain that the deterministic detector flagged this pattern
for analyst review. Do not independently determine the result.

Disclaimer:
This alert does not establish that financial crime occurred.

IMPORTANT:
The five factual labels must appear exactly as written.
Use the exact values from the verified facts.
"""

    user_prompt = f"""
VERIFIED FACTS:

{json.dumps(facts, ensure_ascii=False)}

{correction}
"""

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0,
        response_format={
            "type": "json_object"
        }
    )

    result = json.loads(
        response.choices[0].message.content
    )

    explanation = result.get("explanation", "")

    if not isinstance(explanation, str) or not explanation.strip():
        raise ValueError("LLM returned an empty explanation.")

    return {
        "explanation": explanation,
        "usage": (
            response.usage.model_dump()
            if response.usage else None
        )
    }
