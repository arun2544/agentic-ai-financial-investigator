
from app.services.validator import extract_info, check_claims


def test_extract_info():
    explanation = """
Account ID: ACC-1001
Transaction Count: 4 transactions
Total Amount: ₹52,500
Threshold: ₹50,000
Time Window: 72 hours
"""

    extracted = extract_info(explanation)

    assert extracted == {
        "account_id": "ACC-1001",
        "transaction_count": 4,
        "total_amount": 52500,
        "threshold": 50000,
        "window_hours": 72
    }


def test_mismatched_values():
    facts = {
        "account_id": "ACC-1001",
        "transaction_count": 4,
        "total_amount": 52500,
        "threshold": 50000,
        "window_hours": 72
    }

    claims = {
        "account_id": "ACC-1001",
        "transaction_count": 4,
        "total_amount": 50000,
        "threshold": 52500,
        "window_hours": 72
    }

    result = check_claims(facts, claims)

    assert result["is_valid"] is False
    assert set(result["mismatches"].keys()) == {
        "total_amount", "threshold"
    }


def test_matching_values():
    facts = {
        "account_id": "ACC-1001",
        "transaction_count": 4,
        "total_amount": 52500,
        "threshold": 50000,
        "window_hours": 72
    }

    result = check_claims(facts, facts.copy())

    assert result["is_valid"] is True
    assert result["mismatches"] == {}


def test_missing_claim():
    facts = {
        "account_id": "ACC-1001",
        "total_amount": 52500
    }

    claims = {
        "account_id": "ACC-1001",
        "total_amount": None
    }

    result = check_claims(facts, claims)

    assert result["is_valid"] is False
    assert "total_amount" in result["mismatches"]


def test_duplicate_field():
    explanation = """
Account ID: ACC-1001
Account ID: ACC-2002
Transaction Count: 4 transactions
Total Amount: ₹52,500
Threshold: ₹50,000
Time Window: 72 hours
"""

    extracted = extract_info(explanation)

    assert extracted["account_id"] is None

