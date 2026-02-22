from backend.utils.sanitizer import SovereignDataShield

print("--- Data Sovereignty Redaction Test ---")

# Test Cases
cases = [
    "User wants advice on a 10,000,000 EGP gold investment.",
    "Is it smart to buy 500k USD of gold bars right now?",
    "I have 500 AED, what should I buy?",
    "The year is 2026, and 24k gold is soaring."
]

for c in cases:
    redacted = SovereignDataShield.redact_financials(c)
    print(f"\nOriginal: {c}")
    print(f"Redacted: {redacted}")
