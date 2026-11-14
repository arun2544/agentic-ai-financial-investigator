from datetime import timedelta


def detect_account_patterns(
    transactions,
    account_id,
    threshold=50000,
    window_hours=72,
    min_transaction_count=3
):

    rows = []

    for tx in transactions:

        if tx["account_id"] != account_id:
            continue

        if tx["transaction_type"].upper() != "CREDIT":
            continue

        amount = float(tx["amount"])

        # Only individually below-threshold transactions
        if amount >= threshold:
            continue

        timestamp = tx["timestamp"]

        if hasattr(timestamp, "to_pydatetime"):
            timestamp = timestamp.to_pydatetime()

        rows.append({
            "transaction_id": tx["transaction_id"],
            "timestamp": timestamp,
            "amount": amount
        })

    rows.sort(key=lambda x: x["timestamp"])

    window = timedelta(hours=window_hours)

    patterns = []

    for end_idx, end_tx in enumerate(rows):

        start_idx = end_idx

        while (
            start_idx > 0
            and end_tx["timestamp"] - rows[start_idx - 1]["timestamp"]
            <= window
        ):
            start_idx -= 1

        candidates = rows[start_idx:end_idx + 1]

        total = sum(x["amount"] for x in candidates)

        if (
            len(candidates) >= min_transaction_count
            and total > threshold
        ):

            patterns.append({
                "transactions": candidates,
                "transaction_count": len(candidates),
                "total_amount": total,
                "window_start": candidates[0]["timestamp"],
                "window_end": end_tx["timestamp"]
            })

    if not patterns:

        return {
            "account_id": account_id,
            "is_flagged": False,
            "reason": "No suspicious pattern detected."
        }

    best = max(
        patterns,
        key=lambda x: (
            x["total_amount"],
            x["transaction_count"]
        )
    )

    actual_window = (
        best["window_end"] - best["window_start"]
    ).total_seconds() / 3600

    return {
        "account_id": account_id,
        "is_flagged": True,
        "evidence": {
            "account_id": account_id,
            "transaction_count": best["transaction_count"],
            "total_amount": round(best["total_amount"], 2),
            "threshold": float(threshold),
            "window_hours": round(actual_window, 2),
            "transaction_ids": [
                x["transaction_id"]
                for x in best["transactions"]
            ]
        }
    }
