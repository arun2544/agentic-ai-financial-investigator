from datetime import datetime, timezone
from app.services.detector import detect_account_patterns


def test_detect_structuring_pattern():
    transactions = [
        {
            "transaction_id": "T1001",
            "account_id": "ACC-1001",
            "timestamp": datetime(2026, 11, 10, 9, 0, tzinfo=timezone.utc),
            "transaction_type": "CREDIT",
            "amount": 12000,
        },
        {
            "transaction_id": "T1002",
            "account_id": "ACC-1001",
            "timestamp": datetime(2026, 11, 10, 11, 0, tzinfo=timezone.utc),
            "transaction_type": "CREDIT",
            "amount": 13000,
        },
        {
            "transaction_id": "T1003",
            "account_id": "ACC-1001",
            "timestamp": datetime(2026, 11, 10, 14, 0, tzinfo=timezone.utc),
            "transaction_type": "CREDIT",
            "amount": 14000,
        },
        {
            "transaction_id": "T1004",
            "account_id": "ACC-1001",
            "timestamp": datetime(2026, 11, 10, 18, 0, tzinfo=timezone.utc),
            "transaction_type": "CREDIT",
            "amount": 13500,
        },
    ]

    result = detect_account_patterns(transactions, "ACC-1001")
    assert result["is_flagged"] is True
    assert result["evidence"]["total_amount"] == 52500.0
    assert result["evidence"]["transaction_count"] == 4
    assert result["evidence"]["window_hours"] == 9.0


def test_below_threshold_not_flagged():
    transactions = [
        {
            "transaction_id": "T2001",
            "account_id": "ACC-2002",
            "timestamp": datetime(2026, 11, 10, 9, 0, tzinfo=timezone.utc),
            "transaction_type": "CREDIT",
            "amount": 10000,
        },
        {
            "transaction_id": "T2002",
            "account_id": "ACC-2002",
            "timestamp": datetime(2026, 11, 10, 12, 0, tzinfo=timezone.utc),
            "transaction_type": "CREDIT",
            "amount": 12000,
        },
    ]

    result = detect_account_patterns(transactions, "ACC-2002")
    assert result["is_flagged"] is False
