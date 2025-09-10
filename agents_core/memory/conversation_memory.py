"""Conversation memory management using Redis."""

import json
import redis
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from agents_core.config.settings import settings


class ConversationMemory:
    """Manages conversation memory using Redis."""
    
    def __init__(self):
        self.redis_client = None
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection."""
        try:
            redis_url = settings.get_redis_url_for_memory()
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            print("✅ Redis connected successfully")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Check if Redis is available."""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def _get_session_key(self, session_id: str, tenant_id: str) -> str:
        """Generate Redis key for session."""
        return f"conversation:{tenant_id}:{session_id}"
    
    def _get_summary_key(self, session_id: str, tenant_id: str) -> str:
        """Generate Redis key for session summary."""
        return f"summary:{tenant_id}:{session_id}"
    
    def add_message(self, 
                   session_id: str, 
                   tenant_id: str,
                   role: str,  # 'user' or 'assistant'
                   content: str,
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add a message to conversation history."""
        if not self.is_available():
            return False
        
        try:
            key = self._get_session_key(session_id, tenant_id)
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            # Add to list (FIFO)
            self.redis_client.lpush(key, json.dumps(message))
            
            # Keep only last 20 messages
            self.redis_client.ltrim(key, 0, 19)
            
            # Set expiry (7 days)
            self.redis_client.expire(key, 60 * 60 * 24 * 7)
            
            return True
        except Exception as e:
            print(f"❌ Failed to add message to memory: {e}")
            return False
    
    def get_conversation_history(self, 
                               session_id: str, 
                               tenant_id: str,
                               limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history."""
        if not self.is_available():
            return []
        
        try:
            key = self._get_session_key(session_id, tenant_id)
            messages = self.redis_client.lrange(key, 0, limit - 1)
            
            history = []
            for msg_str in reversed(messages):  # Reverse to get chronological order
                try:
                    msg = json.loads(msg_str)
                    history.append(msg)
                except json.JSONDecodeError:
                    continue
            
            return history
        except Exception as e:
            print(f"❌ Failed to get conversation history: {e}")
            return []
    
    def get_conversation_summary(self, 
                               session_id: str, 
                               tenant_id: str) -> str:
        """Get conversation summary."""
        if not self.is_available():
            return ""
        
        try:
            key = self._get_summary_key(session_id, tenant_id)
            summary = self.redis_client.get(key)
            return summary or ""
        except Exception as e:
            print(f"❌ Failed to get conversation summary: {e}")
            return ""
    
    def update_conversation_summary(self, 
                                  session_id: str, 
                                  tenant_id: str,
                                  summary: str) -> bool:
        """Update conversation summary."""
        if not self.is_available():
            return False
        
        try:
            key = self._get_summary_key(session_id, tenant_id)
            self.redis_client.set(key, summary, ex=60 * 60 * 24 * 7)  # 7 days
            return True
        except Exception as e:
            print(f"❌ Failed to update conversation summary: {e}")
            return False
    
    def generate_context_summary(self, 
                                session_id: str, 
                                tenant_id: str) -> str:
        """Generate a context summary from recent messages."""
        history = self.get_conversation_history(session_id, tenant_id, limit=6)
        
        if not history:
            return ""
        
        # Simple summarization logic
        user_messages = [msg["content"] for msg in history if msg["role"] == "user"]
        assistant_messages = [msg["content"] for msg in history if msg["role"] == "assistant"]
        
        if not user_messages:
            return ""
        
        # Create a simple context summary
        context_parts = []
        
        if len(user_messages) > 1:
            context_parts.append(f"User has asked about: {', '.join(user_messages[-3:])}")
        
        if assistant_messages:
            last_response = assistant_messages[-1]
            if len(last_response) > 100:
                last_response = last_response[:100] + "..."
            context_parts.append(f"Last discussed: {last_response}")
        
        return " | ".join(context_parts)
    
    def clear_session(self, session_id: str, tenant_id: str) -> bool:
        """Clear all memory for a session."""
        if not self.is_available():
            return False
        
        try:
            session_key = self._get_session_key(session_id, tenant_id)
            summary_key = self._get_summary_key(session_id, tenant_id)
            
            self.redis_client.delete(session_key)
            self.redis_client.delete(summary_key)
            
            return True
        except Exception as e:
            print(f"❌ Failed to clear session: {e}")
            return False


# Global memory instance
conversation_memory = ConversationMemory()
