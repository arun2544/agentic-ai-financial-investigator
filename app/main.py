
import json

from app.services.data_service import load_transactions
from app.services.detector import detect_account_patterns
from app.services.evidence import build_claim_facts

from app.agents.workflow import run_explanation_workflow
from app.core.config import settings


def investigate_account(account_id):

    print("\n========== FINANCIAL CRIME INVESTIGATION ==========")

    # STEP 1: Load transaction dataset
    print("\n[1] Loading transaction dataset...")

    transactions = load_transactions()

    print(f"Total transactions loaded: {len(transactions)}")

    # STEP 2: Run deterministic detector
    print("\n[2] Running transaction detector...")

    detection = detect_account_patterns(
        transactions,
        account_id,
        threshold=settings.threshold,
        window_hours=settings.window_hours,
        min_transaction_count=settings.min_transaction_count
    )

    if not detection["is_flagged"]:

        print("\nAccount not flagged.")
        print("Reason:", detection["reason"])

        return

    print("\nSuspicious transaction pattern detected.")

    # STEP 3: Build trusted evidence
    print("\n[3] Building trusted evidence...")

    facts = build_claim_facts(detection)

    print(json.dumps(facts, indent=4))

    # STEP 4: Run Agentic AI explanation workflow
    print("\n[4] Starting LLM explanation and validation workflow...")

    report = run_explanation_workflow(facts)

    # STEP 5: Display final report
    print("\n========== INVESTIGATION REPORT ==========")

    print("\nStatus:", report["status"])

    print("\nExplanation:")
    print(report["explanation"] or "No verified explanation available.")

    print("\nExtracted Information:")
    print(json.dumps(report["extracted_info"], indent=4))

    print("\nValidation Mismatches:")
    print(json.dumps(report["mismatches"], indent=4))

    print("\nTotal Attempts:", report["attempts"])

    print("\nValidation History:")
    print(json.dumps(report["validation_history"], indent=4))

    print("\n===========================================")

    return report


if __name__ == "__main__":

    account_id = input(
        "\nEnter Account ID (e.g. ACC-1001): "
    ).strip().upper()

    if not account_id:
        print("Please enter a valid account ID.")
    else:
        investigate_account(account_id)
