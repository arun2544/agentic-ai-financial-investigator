# Agentic AI Financial Crime Investigator

An Agentic AI-based financial crime investigation project that combines
deterministic transaction-pattern detection, LLM-generated explanations,
local claim extraction, evidence validation, and a LangGraph retry
workflow.

> **Important:** A detected pattern is an alert for analyst review. It
> does not establish that financial crime has occurred.

## Overview

The application accepts an account ID, loads transaction records from a
CSV file, and checks the selected account for a configured structuring
pattern. If the detector flags the account, the system builds trusted
evidence and asks a Groq-hosted LLM to generate an investigation
explanation.

The generated explanation is then checked locally using Python regular
expressions. Extracted factual fields are compared against the detector
evidence. If values are missing or inconsistent, LangGraph can request a
corrected explanation, up to the configured retry limit. If validation
still fails, the result is marked for human review.

## Architecture

``` mermaid
flowchart TD
    A["User enters Account ID"] --> B["main.py"]
    B --> C["data_service.py<br/>Load transactions.csv"]
    C --> D["detector.py<br/>Deterministic pattern detection"]
    D --> E{"Pattern flagged?"}
    E -- "No" --> F["Print not-flagged reason<br/>Stop"]
    E -- "Yes" --> G["evidence.py<br/>Build trusted evidence"]
    G --> H["LangGraph workflow"]
    H --> I["Generate explanation<br/>llm_agent.py / Groq"]
    I --> J["Extract claims<br/>validator.py / Regex"]
    J --> K["Validate claims<br/>against trusted evidence"]
    K --> L{"All extracted fields match?"}
    L -- "Yes" --> M["Validated investigation report"]
    L -- "No, attempts remain" --> N["Send mismatch feedback"]
    N --> I
    L -- "No, retry limit reached" --> O["Needs human review"]
```

## Investigation workflow

1.  **Load transactions** -- `data_service.py` reads
    `data/transactions.csv`.
2.  **Detect a pattern** -- `detector.py` applies deterministic rules to
    the selected account. The current structuring rule considers
    qualifying credit transactions, a minimum transaction count, a
    cumulative amount threshold, and a rolling time window.
3.  **Build trusted evidence** -- `evidence.py` creates the factual
    values used as the source of truth for the explanation.
4.  **Generate an explanation** -- `llm_agent.py` calls the configured
    Groq model to produce a human-readable explanation from the trusted
    evidence.
5.  **Extract claims locally** -- `validator.py` uses regular
    expressions to extract the expected labelled fields from the actual
    LLM explanation. This step does not require another LLM API call.
6.  **Validate claims** -- extracted values are compared with trusted
    evidence.
7.  **Retry or route to review** -- LangGraph retries explanation
    generation with mismatch feedback while attempts remain. If
    validation continues to fail, the workflow returns
    `needs_human_review`.

### Current claim-validation scope

The current validator checks these labelled fields:

-   Account ID
-   Transaction count
-   Total amount
-   Threshold
-   Time window

A successful validation means these extracted fields match the trusted
evidence. It does **not** independently prove that every sentence in the
free-form narrative is factually correct. Narrative-level verification
is a potential future improvement.

## Project structure

``` text
agaent_for_finance/
├── app/
│   ├── agents/
│   │   ├── llm_agent.py
│   │   └── workflow.py
│   ├── core/
│   │   └── config.py
│   ├── services/
│   │   ├── data_service.py
│   │   ├── detector.py
│   │   ├── evidence.py
│   │   └── validator.py
│   └── main.py
├── data/
│   └── transactions.csv
├── tests/
│   ├── test_detector.py
│   └── test_validator.py
├── .env                 # local secret configuration; do not commit
├── .gitignore
├── README.md
└── requirements.txt
```

## Configuration

The current sample detector configuration discussed for this project is:

  Parameter                           Example value
  --------------------------------- ---------------
  Amount threshold                          ₹50,000
  Rolling time window                      72 hours
  Minimum qualifying transactions                 3

These values should be read from the project's configuration and can be
changed there. The observed transaction span in the evidence is the span
between the qualifying transactions selected by the detector; it is not
necessarily the configured maximum window.

## Example scenarios in the sample dataset

The sample CSV includes accounts designed to exercise different outcomes
under the current structuring rule:

  -----------------------------------------------------------------------
  Account                 Scenario                Expected detector
                                                  outcome
  ----------------------- ----------------------- -----------------------
  `ACC-1001`              Four credits totalling  Flagged
                          ₹52,500 within 9 hours  

  `ACC-2002`              Two credits and one     Not flagged
                          debit                   

  `ACC-3003`              One credit of ₹60,000   Not flagged by this
                                                  structuring rule

  `ACC-4004`              Three credits totalling Flagged
                          ₹55,000                 

  `ACC-5005`              Three credits totalling Not flagged
                          ₹48,000                 

  `ACC-6006`              Credits spread beyond   Not flagged
                          the 72-hour window      

  `ACC-7007`              Debit is excluded;      Not flagged
                          qualifying credits      
                          total ₹41,000           

  `ACC-8008`              One credit of ₹75,000   Not flagged by this
                                                  structuring rule

  `ACC-9009`              Two credits totalling   Not flagged
                          ₹65,000                 

  `ACC-1010`              Four credits totalling  Flagged
                          ₹56,000                 
  -----------------------------------------------------------------------

**Interpretation:** "Not flagged" means only that this particular rule
did not detect a qualifying pattern. It does not mean the account or
transactions are legitimate. For example, a single large credit may
require a separate large-transaction rule.

## Tech stack

-   **Python** -- application logic and deterministic detection
-   **Groq API** -- LLM explanation generation
-   **LangGraph** -- workflow orchestration, state transitions, and
    retry routing
-   **Regular expressions** -- local extraction of labelled claims
-   **Pytest** -- unit testing

The configured model is controlled through the project's
environment/configuration settings. Do not hard-code API keys in source
files.

## Setup

### 1. Clone the repository

``` bash
git clone https://github.com/arun2544/agentic-ai-financial-investigator.git
cd agentic-ai-financial-investigator
```

### 2. Create and activate a virtual environment

Windows PowerShell:

``` powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

``` powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file using the variable names expected by
`app/core/config.py` and `app/agents/llm_agent.py`. Add your own Groq
API key and configured model name.

**Never commit `.env` or expose your API key.**

### 5. Run the application

Run from the repository root:

``` powershell
python -m app.main
```

When prompted, enter an account ID, for example:

``` text
ACC-1001
```

Use `python -m app.main` rather than running `app/main.py` directly, so
package imports resolve from the project root.

## Run tests

From the repository root:

``` powershell
python -m pytest -v
```

## Security and data notes

-   Keep `.env`, API keys, virtual environments, and local caches out of
    Git.
-   The included CSV is sample data for development and testing. Do not
    add real customer or account information to a public repository.
-   A flagged result is an investigation lead, not a conclusion of
    criminal activity.
-   Human review is required when the configured validation workflow
    cannot validate the extracted claims.

## Current limitations and future improvements

-   Extend validation beyond the five labelled fields to cover factual
    statements in the free-form narrative.
-   Add separate detection rules for large individual transactions and
    other typologies.
-   Add more test cases for edge conditions, overlapping rolling
    windows, malformed records, and duplicate transactions.
-   Persist investigation reports and validation history for
    auditability.
-   Add analyst review and case-management functionality.

## Repository

[GitHub:
arun2544/agentic-ai-financial-investigator](https://github.com/arun2544/agentic-ai-financial-investigator)

