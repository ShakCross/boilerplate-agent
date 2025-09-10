"""Input validation and filtering guardrails."""

import re
from typing import Dict, List, Tuple, Optional
from agents_core.config.settings import settings


class InputGuardrails:
    """Input validation and safety checks."""
    
    def __init__(self):
        # Prompt injection patterns
        self.injection_patterns = [
            r"ignore\s+previous\s+instructions",
            r"forget\s+everything\s+above",
            r"you\s+are\s+now\s+a\s+different",
            r"system\s*:\s*you\s+are",
            r"new\s+instructions\s*:",
            r"act\s+as\s+a\s+different",
            r"pretend\s+to\s+be",
            r"roleplay\s+as",
            r"simulate\s+being"
        ]
        
        # Inappropriate content patterns
        self.inappropriate_patterns = [
            r"\b(hack|exploit|bypass|jailbreak)\b",
            r"\b(password|credential|token|api[_\s]?key)\b",
            r"\b(illegal|criminal|fraud|scam)\b"
        ]
        
        # PII patterns
        self.pii_patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
            r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",  # Credit card
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"  # Email (basic)
        ]
    
    def validate_input(self, text: str, session_id: str) -> Tuple[bool, str, Dict[str, any]]:
        """
        Validate input text for safety and appropriateness.
        
        Returns:
            Tuple of (is_valid, filtered_text, metadata)
        """
        metadata = {
            "original_length": len(text),
            "checks_performed": [],
            "flags": []
        }
        
        # Length check
        if len(text) > 2000:
            metadata["flags"].append("too_long")
            return False, "", metadata
        
        if len(text.strip()) < 1:
            metadata["flags"].append("empty")
            return False, "", metadata
        
        metadata["checks_performed"].append("length")
        
        # Prompt injection detection
        injection_detected = self._check_prompt_injection(text.lower())
        if injection_detected:
            metadata["flags"].append("prompt_injection")
            metadata["injection_patterns"] = injection_detected
            return False, "", metadata
        
        metadata["checks_performed"].append("prompt_injection")
        
        # Inappropriate content detection
        inappropriate_detected = self._check_inappropriate_content(text.lower())
        if inappropriate_detected:
            metadata["flags"].append("inappropriate_content")
            metadata["inappropriate_patterns"] = inappropriate_detected
            return False, "", metadata
        
        metadata["checks_performed"].append("inappropriate_content")
        
        # PII detection and masking
        filtered_text, pii_found = self._mask_pii(text)
        if pii_found:
            metadata["flags"].append("pii_detected")
            metadata["pii_masked"] = True
        
        metadata["checks_performed"].append("pii_detection")
        metadata["final_length"] = len(filtered_text)
        
        return True, filtered_text, metadata
    
    def _check_prompt_injection(self, text: str) -> List[str]:
        """Check for prompt injection patterns."""
        found_patterns = []
        for pattern in self.injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                found_patterns.append(pattern)
        return found_patterns
    
    def _check_inappropriate_content(self, text: str) -> List[str]:
        """Check for inappropriate content patterns."""
        found_patterns = []
        for pattern in self.inappropriate_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                found_patterns.append(pattern)
        return found_patterns
    
    def _mask_pii(self, text: str) -> Tuple[str, bool]:
        """Mask PII in text."""
        filtered_text = text
        pii_found = False
        
        # Mask SSN
        if re.search(self.pii_patterns[0], text):
            filtered_text = re.sub(self.pii_patterns[0], "***-**-****", filtered_text)
            pii_found = True
        
        # Mask credit card numbers
        if re.search(self.pii_patterns[1], text):
            filtered_text = re.sub(self.pii_patterns[1], "**** **** **** ****", filtered_text)
            pii_found = True
        
        # Mask emails (partial)
        def mask_email(match):
            email = match.group(0)
            username, domain = email.split('@', 1)
            masked_username = username[0] + '*' * (len(username) - 2) + username[-1] if len(username) > 2 else username
            return f"{masked_username}@{domain}"
        
        if re.search(self.pii_patterns[2], text):
            filtered_text = re.sub(self.pii_patterns[2], mask_email, filtered_text)
            pii_found = True
        
        return filtered_text, pii_found


class OutputGuardrails:
    """Output validation and filtering."""
    
    def __init__(self):
        # Patterns that should not appear in responses
        self.forbidden_patterns = [
            r"i\s+am\s+an?\s+ai\s+language\s+model",
            r"as\s+an?\s+ai\s+assistant",
            r"i\s+don't\s+have\s+access\s+to\s+real[_\s]?time",
            r"i\s+can't\s+browse\s+the\s+internet",
            r"my\s+knowledge\s+cutoff",
            r"i\s+am\s+chatgpt"
        ]
        
        # Confidence thresholds
        self.min_confidence = 0.3
        self.low_confidence_threshold = 0.7
    
    def validate_output(self, 
                       text: str, 
                       confidence: float,
                       tools_used: List[str],
                       metadata: Dict[str, any]) -> Tuple[bool, str, Dict[str, any]]:
        """
        Validate and potentially modify output.
        
        Returns:
            Tuple of (is_valid, modified_text, metadata)
        """
        validation_metadata = {
            "original_confidence": confidence,
            "original_length": len(text),
            "checks_performed": [],
            "modifications": []
        }
        
        # Confidence check
        if confidence < self.min_confidence:
            validation_metadata["flags"] = ["low_confidence"]
            fallback_text = "I'm not confident in my response to that question. Could you please rephrase or provide more details?"
            return True, fallback_text, validation_metadata
        
        validation_metadata["checks_performed"].append("confidence")
        
        # Remove forbidden patterns
        modified_text = text
        for pattern in self.forbidden_patterns:
            if re.search(pattern, modified_text, re.IGNORECASE):
                # Replace with more professional alternatives
                if "ai language model" in pattern or "ai assistant" in pattern:
                    modified_text = re.sub(pattern, "a professional assistant", modified_text, flags=re.IGNORECASE)
                elif "don't have access to real" in pattern:
                    modified_text = re.sub(pattern, "don't have current", modified_text, flags=re.IGNORECASE)
                else:
                    modified_text = re.sub(pattern, "", modified_text, flags=re.IGNORECASE)
                validation_metadata["modifications"].append(f"removed_pattern: {pattern}")
        
        validation_metadata["checks_performed"].append("forbidden_patterns")
        
        # Length validation
        if len(modified_text.strip()) < 10:
            validation_metadata["flags"] = ["too_short"]
            fallback_text = "I apologize, but I couldn't generate an appropriate response. Could you please try rephrasing your question?"
            return True, fallback_text, validation_metadata
        
        validation_metadata["checks_performed"].append("length")
        validation_metadata["final_length"] = len(modified_text)
        
        # Add low confidence disclaimer if needed
        if confidence < self.low_confidence_threshold:
            modified_text += "\\n\\n*Note: I'm not entirely certain about this response. Please verify the information if it's important.*"
            validation_metadata["modifications"].append("added_uncertainty_disclaimer")
        
        return True, modified_text.strip(), validation_metadata


# Global instances
input_guardrails = InputGuardrails()
output_guardrails = OutputGuardrails()
