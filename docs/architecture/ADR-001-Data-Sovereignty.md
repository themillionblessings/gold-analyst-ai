# Architecture Decision Record
# ADR 001: Data Sovereignty & PII Redaction Strategy

## Status
Accepted

## Context
The "Gold Analyst AI" platform processes queries from users, potentially including highly sensitive financial data (e.g., "I am selling 10,000,000 EGP worth of gold bars in Cairo"). Under strict MENA data localization laws (such as the UAE Federal Decree-Law No. 45 of 2021 on Personal Data Protection), transmitting unredacted financial or personal data to globally hosted LLM endpoints (like Google Gemini or OpenAI) poses a severe non-compliance risk.

Currently, the system relies on external LLMs to perform sentiment analysis and deal evaluation.

## Decision
We implemented a robust middle-layer utility, **`SovereignDataShield`**, to intercept and sanitize all outgoing prompts *before* they exit the secured environment.

1. **Regex Redaction:** The shield identifies highly specific financial patterns (currencies, large numbers).
2. **Data Tiering:** Instead of a generic `[REDACTED]`, the shield substitutes amounts with contextual tiers (e.g., `[REDACTED_CAPITAL_TIER_3]`). This preserves the semantic context required for the LLM to provide high-quality analysis ("This is a massive institutional deal") without violating data privacy by revealing the exact figure.

## Future Target Architecture
While `SovereignDataShield` mitigates immediate compliance risks for cloud LLMs, our production Phase 3 objective is to eliminate external data transfer entirely. 

In future iterations, we will transition the core analytical reasoning engine to a localized LLM (e.g., Llama 3 or Mistral) hosted directly within the region—specifically targeting deployment on **Azure UAE North**. This will guarantee 100% data sovereignty for our Gulf and Egyptian user base.

## Consequences
- **Positive:** Immediate compliance with regional data protection mandates.
- **Positive:** The LLM still receives the context needed to provide accurate analysis via the Tier system.
- **Negative:** Slight overhead in string processing latency.
- **Negative:** Edge cases exist where non-financial numbers might be mistakenly redacted if they match the currency heuristics.
