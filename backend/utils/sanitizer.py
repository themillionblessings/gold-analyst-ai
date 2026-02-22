import re
import logging

logger = logging.getLogger(__name__)

class SovereignDataShield:
    """
    Data Sovereignty & PII Sanitizer for MENA Compliance (UAE/KSA).
    Detects and redacts large financial figures before transmission to external LLMs.
    """
    
    # Regex to match currency amounts: $10,000, 500k, 10M, 5,000,000 EGP, 200 AED
    # It looks for optional currency symbols, then numbers with optional commas/decimals, 
    # followed optionally by k/m/b or currency codes.
    FINANCIAL_PATTERN = re.compile(
        r'(?:USD|EGP|AED|\$|£|€)?\s*'                  # Optional prefix
        r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b'            # The number itself (e.g., 10,000.50)
        r'\s*(?:k|m|b|million|billion|thousand|USD|EGP|AED)?', # Optional suffix
        re.IGNORECASE
    )

    @classmethod
    def categorize_tier(cls, amount_str: str) -> str:
        """
        Estimates the scale of the number to provide context to the LLM without leaking PII.
        """
        # Remove non-numeric characters for rough evaluation
        clean_num = re.sub(r'[^\d.]', '', amount_str)
        try:
            val = float(clean_num)
            if val < 10000:
                return "[REDACTED_CAPITAL_TIER_1]"   # Small retail
            elif val < 1000000:
                return "[REDACTED_CAPITAL_TIER_2]"   # Medium investment
            else:
                return "[REDACTED_CAPITAL_TIER_3]"   # Large/Institutional deal
        except ValueError:
            return "[REDACTED_FINANCIAL_DATA]"

    @classmethod
    def redact_financials(cls, text: str) -> str:
        """
        Scans block of text and replaces specific large currency amounts with redacted Tier tokens.
        """
        if not text:
            return text
            
        def replacer(match):
            original = match.group(0)
            # Only redact if it looks like a substantial number (rough proxy: contains a comma, k/m/b, or currency code)
            # This prevents redacting standard years like "2026" or "24k" gold markers.
            if any(marker in original.lower() for marker in [',', 'k', 'm', 'b', 'usd', 'egp', 'aed', '$']):
                tier = cls.categorize_tier(original)
                logger.debug(f"SovereignDataShield: Redacted '{original}' -> {tier}")
                return f" {tier} "
            return original

        redacted_text = cls.FINANCIAL_PATTERN.sub(replacer, text)
        return redacted_text
