"""Langfuse integration for observability."""

import os
from typing import Dict, Any, Optional
from langfuse import Langfuse
from agents_core.config.settings import settings


class LangfuseClient:
    """Centralized Langfuse client for observability."""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Langfuse client if credentials are available."""
        try:
            if (settings.langfuse_public_key and 
                settings.langfuse_secret_key and 
                settings.langfuse_host):
                
                self.client = Langfuse(
                    public_key=settings.langfuse_public_key,
                    secret_key=settings.langfuse_secret_key,
                    host=settings.langfuse_host
                )
                # Verificar autenticación
                auth_ok = self.client.auth_check()
                if auth_ok:
                    print("✅ Langfuse client initialized and authenticated successfully")
                else:
                    print("❌ Langfuse authentication failed")
                    self.client = None
            else:
                print("⚠️ Langfuse credentials not configured")
        except Exception as e:
            print(f"❌ Failed to initialize Langfuse: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Langfuse is available."""
        return self.client is not None
    
    def create_trace(self, 
                    name: str, 
                    user_id: Optional[str] = None,
                    session_id: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Create a new trace in Langfuse."""
        if not self.is_available():
            return None
        
        try:
            # Generate a unique trace ID
            trace_id = self.client.create_trace_id()
            
            # Create a simple event to mark trace start
            self.client.create_event(
                name=f"{name}_started",
                input={"user_id": user_id, "session_id": session_id},
                metadata={
                    **(metadata or {}),
                    "event_type": "trace_start",
                    "trace_name": name
                }
            )
            return trace_id
        except Exception as e:
            print(f"❌ Failed to create Langfuse trace: {e}")
            return None
    
    def create_span(self, 
                   trace_id: str,
                   name: str,
                   input_data: Optional[Dict[str, Any]] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Create a span within a trace."""
        if not self.is_available():
            return None
        
        try:
            # Create a simple event for the span
            self.client.create_event(
                name=f"{name}_span",
                input=input_data or {},
                metadata={
                    **(metadata or {}),
                    "event_type": "span",
                    "trace_id": trace_id
                }
            )
            return trace_id
        except Exception as e:
            print(f"❌ Failed to create Langfuse span: {e}")
            return None
    
    def log_generation(self,
                      trace_id: str,
                      name: str,
                      input_data: Optional[Dict[str, Any]] = None,
                      output_data: Optional[Dict[str, Any]] = None,
                      model: Optional[str] = None,
                      usage: Optional[Dict[str, Any]] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Log an LLM generation."""
        if not self.is_available():
            return None
        
        try:
            # Create a simple event for the generation
            self.client.create_event(
                name=f"{name}_generation",
                input=input_data or {},
                output=output_data or {},
                metadata={
                    **(metadata or {}),
                    "event_type": "llm_generation",
                    "model": model or "unknown",
                    "usage": usage or {},
                    "trace_id": trace_id
                }
            )
            return trace_id
        except Exception as e:
            print(f"❌ Failed to log Langfuse generation: {e}")
            return None
    
    def flush(self):
        """Flush pending events to Langfuse."""
        if self.is_available():
            try:
                self.client.flush()
            except Exception as e:
                print(f"❌ Failed to flush Langfuse events: {e}")


# Global Langfuse client instance
langfuse_client = LangfuseClient()


def trace_conversation(session_id: str, tenant_id: str):
    """Decorator to trace entire conversations."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not langfuse_client.is_available():
                return func(*args, **kwargs)
            
            trace_id = langfuse_client.create_trace(
                name="conversation",
                session_id=session_id,
                metadata={
                    "tenant_id": tenant_id,
                    "function": func.__name__
                }
            )
            
            try:
                result = func(*args, **kwargs)
                
                # Log successful completion event
                if trace_id and langfuse_client.is_available():
                    langfuse_client.client.create_event(
                        name="conversation_completed",
                        output={"success": True},
                        metadata={
                            "completed": True,
                            "trace_id": trace_id
                        }
                    )
                
                return result
            except Exception as e:
                # Log error event
                if trace_id and langfuse_client.is_available():
                    langfuse_client.client.create_event(
                        name="conversation_error",
                        output={"error": str(e)},
                        metadata={
                            "error": True,
                            "trace_id": trace_id
                        }
                    )
                raise
            finally:
                langfuse_client.flush()
        
        return wrapper
    return decorator


def trace_agent_run(trace_id: str, message: str, model: str):
    """Trace an agent run."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if not langfuse_client.is_available():
                return await func(*args, **kwargs)
            
            span_id = langfuse_client.create_span(
                trace_id=trace_id,
                name="agent_run",
                input_data={"message": message, "model": model}
            )
            
            try:
                result = await func(*args, **kwargs)
                
                # Log completion event
                if span_id and langfuse_client.is_available():
                    langfuse_client.client.create_event(
                        name="agent_run_completed",
                        output={
                            "reply": result.get("reply", ""),
                            "confidence": result.get("confidence", 0),
                            "tools_used": result.get("tools_used", [])
                        },
                        metadata={"trace_id": trace_id}
                    )
                
                return result
            except Exception as e:
                # Log error event
                if span_id and langfuse_client.is_available():
                    langfuse_client.client.create_event(
                        name="agent_run_error",
                        output={"error": str(e)},
                        metadata={"trace_id": trace_id}
                    )
                raise
            
        return wrapper
    return decorator
