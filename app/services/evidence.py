def build_claim_facts(detection):

    if not detection["is_flagged"]:
        raise ValueError("Account is not flagged.")

    evidence = detection["evidence"]

    return {
        "account_id": evidence["account_id"],
        "transaction_count": evidence["transaction_count"],
        "total_amount": evidence["total_amount"],
        "threshold": evidence["threshold"],
        "window_hours": evidence["window_hours"]
    }
