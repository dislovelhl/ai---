import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# Basic toxic patterns (simplified for demonstration)
TOXIC_PATTERNS = [
    r"(?i)ignore prev",
    r"(?i)override instructions",
    r"(?i)system prompt",
]

# Sensitive patterns (PII)
PII_PATTERNS = {
    "phone": r"\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
}

class ContentGuardrails:
    """
    Guardrails for input/output safety.
    """
    
    @staticmethod
    def validate_input(text: str) -> Optional[str]:
        """
        Validates user input against safety patterns.
        Returns the sanitized text or raises an error (for demo, returns sanitized).
        """
        if not text:
            return text
            
        for pattern in TOXIC_PATTERNS:
            if re.search(pattern, text):
                logger.warning(f"Guardrail triggered: Potential prompt injection detected in '{text}'")
                return "[REDACTED: Potential Security Risk]"
        
        return text

    @staticmethod
    def sanitize_output(text: str) -> str:
        """
        Sanitizes output (e.g., masking PII).
        """
        if not text:
            return text
            
        sanitized = text
        for category, pattern in PII_PATTERNS.items():
            sanitized = re.sub(pattern, f"[{category.upper()}]", sanitized)
            
        return sanitized

guardrails = ContentGuardrails()
