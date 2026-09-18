"""Cleaning and PII redaction services for crawled text and metadata."""

import html
import re
import unicodedata
from typing import Dict, List, Tuple


class PIIRedactor:
    """Detects and redacts Personally Identifiable Information (PII) and secret credentials."""

    EMAIL_PATTERN = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )
    PHONE_PATTERN = re.compile(
        r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    )
    # Credit cards (Visa, MasterCard, Amex, Discover)
    CREDIT_CARD_PATTERN = re.compile(
        r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12})\b"
        r"|\b(?:\d{4}[-\s]\d{4}[-\s]\d{4}[-\s]\d{4})\b"
    )
    SSN_PATTERN = re.compile(
        r"\b\d{3}-\d{2}-\d{4}\b"
    )
    SECRET_KEY_PATTERN = re.compile(
        r"\b(?:sk_[a-zA-Z0-9_]{16,}|Bearer\s+[A-Za-z0-9._~+/-]{20,}|AKIA[0-9A-Z]{16})\b",
        re.IGNORECASE,
    )

    @classmethod
    def redact(cls, text: str) -> str:
        """Redact sensitive PII and secrets from string."""
        if not text:
            return ""

        redacted = cls.EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
        redacted = cls.PHONE_PATTERN.sub("[REDACTED_PHONE]", redacted)
        redacted = cls.CREDIT_CARD_PATTERN.sub("[REDACTED_CARD]", redacted)
        redacted = cls.SSN_PATTERN.sub("[REDACTED_SSN]", redacted)
        redacted = cls.SECRET_KEY_PATTERN.sub("[REDACTED_SECRET]", redacted)
        return redacted


class CleaningService:
    """Strips remaining markup, normalizes Unicode, unescapes entities, and collapses spaces."""

    TAG_PATTERN = re.compile(r"<[^>]+>")
    WHITESPACE_PATTERN = re.compile(r"[ \t]+")
    MULTILINE_PATTERN = re.compile(r"\n{3,}")

    @classmethod
    def clean_text(cls, raw: str) -> str:
        """Clean raw text, normalize Unicode, strip HTML tags, and redact PII."""
        if not raw:
            return ""

        # 1. Unescape HTML entities
        unescaped = html.unescape(raw)

        # 2. Strip any remaining HTML tags
        no_tags = cls.TAG_PATTERN.sub(" ", unescaped)

        # 3. Unicode normalization
        normalized_unicode = unicodedata.normalize("NFKC", no_tags)

        # 4. Collapse spaces and excessive newlines
        single_spaced = cls.WHITESPACE_PATTERN.sub(" ", normalized_unicode)
        collapsed_lines = cls.MULTILINE_PATTERN.sub("\n\n", single_spaced)
        cleaned = collapsed_lines.strip()

        # 5. Redact PII
        return PIIRedactor.redact(cleaned)
