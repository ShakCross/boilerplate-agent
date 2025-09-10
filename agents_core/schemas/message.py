"""Message schemas and DTOs."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class MessageDTO(BaseModel):
    """Input message data transfer object."""
    
    session_id: str = Field(..., min_length=1, max_length=100, description="Session identifier")
    tenant_id: str = Field(..., pattern=r"^[a-zA-Z0-9_-]+$", description="Tenant identifier")
    text: str = Field(..., min_length=1, max_length=2000, description="User message text")
    locale: str = Field(default="en", pattern=r"^[a-z]{2}$", description="Language locale")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_123",
                "tenant_id": "tenant_abc",
                "text": "Hello, I need help with scheduling a visit",
                "locale": "en"
            }
        }


class AgentResponse(BaseModel):
    """Agent response data transfer object."""
    
    reply: str = Field(..., description="Agent's response text")
    session_id: str = Field(..., description="Session identifier")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Response confidence score")
    tools_used: list[str] = Field(default_factory=list, description="List of tools used in response")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "reply": "I can help you schedule a visit. Please provide the property ID and your preferred date and time.",
                "session_id": "sess_123",
                "confidence": 0.95,
                "tools_used": [],
                "metadata": {"model_used": "gpt-4o-mini", "tokens_used": 45}
            }
        }
