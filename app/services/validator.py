

import re


def extract_info(llm_response: str) -> dict:
    """
    Extract factual claims from the LLM-generated explanation.
    This function runs locally and does not call any LLM API.
    """

    result = {
        "account_id": None,
        "transaction_count": None,
        "total_amount": None,
        "threshold": None,
        "window_hours": None
    }

    if not isinstance(llm_response, str):
        return result

    patterns = {
        "account_id":
            r"^Account ID:\s*(ACC-\d+)\s*$",

        "transaction_count":
            r"^Transaction Count:\s*(\d+)\s+transactions?\s*$",

        "total_amount":
            r"^Total Amount:\s*₹?\s*([\d,]+(?:\.\d+)?)\s*$",

        "threshold":
            r"^Threshold:\s*₹?\s*([\d,]+(?:\.\d+)?)\s*$",

        # Supports both 9 hours and 9.0 hours
        "window_hours":
            r"^Time Window:\s*(\d+(?:\.\d+)?)\s+hours?\s*$"
    }

    for key, pattern in patterns.items():

        matches = re.findall(
            pattern,
            llm_response,
            re.IGNORECASE | re.MULTILINE
        )

        # Reject missing or duplicate fields
        if len(matches) != 1:
            continue

        value = matches[0]

        if key == "account_id":
            result[key] = value.upper()

        elif key == "transaction_count":
            result[key] = int(value)

        else:
            number = float(value.replace(",", ""))

            result[key] = (
                int(number) if number.is_integer() else number
            )

    return result


def check_claims(
    trusted_facts: dict,
    extracted_claims: dict
) -> dict:
    """
    Compare extracted LLM claims against trusted detector evidence.
    """

    mismatches = {}

    for key, expected_value in trusted_facts.items():

        actual_value = extracted_claims.get(key)

        if actual_value is None:

            mismatches[key] = {
                "expected": expected_value,
                "extracted": None,
                "reason": "Missing or unextractable claim"
            }

            continue

        if (
            isinstance(expected_value, (int, float))
            and not isinstance(expected_value, bool)
        ):

            try:
                is_equal = float(expected_value) == float(actual_value)

            except (ValueError, TypeError):
                is_equal = False

        else:
            is_equal = expected_value == actual_value

        if not is_equal:

            mismatches[key] = {
                "expected": expected_value,
                "extracted": actual_value,
                "reason": "Claim does not match detector evidence"
            }

    return {
        "is_valid": len(mismatches) == 0,
        "mismatches": mismatches
    }

