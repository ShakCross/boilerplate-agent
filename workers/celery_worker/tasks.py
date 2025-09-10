"""Celery tasks for background processing."""

import asyncio
from typing import Dict, Any
from celery import current_app as celery_app
from agents_core.orchestrator.agent import run_agent
from agents_core.config.settings import get_tenant_config
from agents_core.memory.conversation_memory import conversation_memory


@celery_app.task(bind=True, name='process_message_async')
def process_message_async(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a message asynchronously using Celery.
    
    Args:
        message_data: Dict containing message, session_id, tenant_id, locale
    
    Returns:
        Dict with processing result
    """
    try:
        # Extract data
        message = message_data['message']
        session_id = message_data['session_id']
        tenant_id = message_data['tenant_id']
        locale = message_data.get('locale', 'en')
        
        # Get tenant config
        tenant_config = get_tenant_config(tenant_id)
        
        # Get conversation context
        session_summary = conversation_memory.generate_context_summary(
            session_id, tenant_id
        )
        
        # Run agent in async context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                run_agent(
                    message=message,
                    session_id=session_id,
                    tenant_config=tenant_config,
                    session_summary=session_summary,
                    language=locale
                )
            )
            
            # Save to memory
            conversation_memory.add_message(
                session_id=session_id,
                tenant_id=tenant_id,
                role="user",
                content=message,
                metadata={"locale": locale}
            )
            
            conversation_memory.add_message(
                session_id=session_id,
                tenant_id=tenant_id,
                role="assistant",
                content=result["reply"],
                metadata={
                    "confidence": result["confidence"],
                    "tools_used": result["tools_used"],
                    "async_processing": True
                }
            )
            
            return {
                "success": True,
                "result": result,
                "task_id": self.request.id
            }
            
        finally:
            loop.close()
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "task_id": self.request.id
        }


@celery_app.task(name='cleanup_old_sessions')
def cleanup_old_sessions() -> Dict[str, Any]:
    """Clean up old conversation sessions."""
    try:
        # This is a placeholder for session cleanup logic
        # In a real implementation, you'd clean up old Redis keys
        print("Running session cleanup task...")
        
        return {
            "success": True,
            "cleaned_sessions": 0,
            "message": "Session cleanup completed"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(name='generate_session_summary')
def generate_session_summary(session_id: str, tenant_id: str) -> Dict[str, Any]:
    """Generate and update session summary."""
    try:
        # Get conversation history
        history = conversation_memory.get_conversation_history(
            session_id, tenant_id, limit=20
        )
        
        if not history:
            return {
                "success": True,
                "message": "No history to summarize"
            }
        
        # Simple summarization logic
        user_messages = [msg["content"] for msg in history if msg["role"] == "user"]
        topics = ", ".join(user_messages[-5:])  # Last 5 user messages
        
        summary = f"Recent topics discussed: {topics}"
        
        # Update summary
        conversation_memory.update_conversation_summary(
            session_id, tenant_id, summary
        )
        
        return {
            "success": True,
            "summary": summary,
            "messages_processed": len(history)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
