"""Webhook management and delivery system."""

import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from agents_core.middleware.rate_limiting import cache_manager


class WebhookEvent(BaseModel):
    """Webhook event data structure."""
    event_type: str = Field(..., description="Type of event (message_processed, error_occurred, etc.)")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    data: Dict[str, Any] = Field(..., description="Event data payload")
    tenant_id: str = Field(..., description="Tenant identifier")
    session_id: Optional[str] = Field(None, description="Session identifier if applicable")


class WebhookSubscription(BaseModel):
    """Webhook subscription configuration."""
    webhook_id: str = Field(..., description="Unique webhook identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    url: str = Field(..., description="Webhook endpoint URL")
    events: List[str] = Field(..., description="List of event types to subscribe to")
    secret: Optional[str] = Field(None, description="Secret for webhook verification")
    enabled: bool = Field(default=True, description="Whether webhook is enabled")
    retry_config: Dict[str, Any] = Field(default={
        "max_retries": 3,
        "retry_delay_seconds": 5,
        "exponential_backoff": True
    })


class WebhookManager:
    """Manage webhook subscriptions and delivery."""
    
    def __init__(self):
        self.cache = cache_manager
        self.session = None
        self._initialize_session()
    
    async def _initialize_session(self):
        """Initialize HTTP session for webhook delivery."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
    
    def add_webhook_subscription(self, subscription: WebhookSubscription) -> bool:
        """Add a new webhook subscription."""
        if not self.cache.is_available():
            return False
        
        try:
            # Store subscription
            webhook_key = f"webhook:{subscription.tenant_id}:{subscription.webhook_id}"
            self.cache.set(
                webhook_key,
                subscription.model_dump_json(),
                ttl=86400 * 30  # 30 days
            )
            
            # Add to tenant's webhook list
            tenant_webhooks_key = f"webhooks:tenant:{subscription.tenant_id}"
            current_webhooks = self.cache.get(tenant_webhooks_key)
            
            if current_webhooks:
                webhook_list = json.loads(current_webhooks)
            else:
                webhook_list = []
            
            if subscription.webhook_id not in webhook_list:
                webhook_list.append(subscription.webhook_id)
                self.cache.set(tenant_webhooks_key, json.dumps(webhook_list), ttl=86400 * 30)
            
            return True
            
        except Exception as e:
            print(f"Failed to add webhook subscription: {e}")
            return False
    
    def get_webhook_subscriptions(self, tenant_id: str) -> List[WebhookSubscription]:
        """Get all webhook subscriptions for a tenant."""
        if not self.cache.is_available():
            return []
        
        try:
            tenant_webhooks_key = f"webhooks:tenant:{tenant_id}"
            webhook_ids = self.cache.get(tenant_webhooks_key)
            
            if not webhook_ids:
                return []
            
            webhook_list = json.loads(webhook_ids)
            subscriptions = []
            
            for webhook_id in webhook_list:
                webhook_key = f"webhook:{tenant_id}:{webhook_id}"
                webhook_data = self.cache.get(webhook_key)
                
                if webhook_data:
                    try:
                        subscription = WebhookSubscription.model_validate_json(webhook_data)
                        subscriptions.append(subscription)
                    except Exception as e:
                        print(f"Failed to parse webhook {webhook_id}: {e}")
            
            return subscriptions
            
        except Exception as e:
            print(f"Failed to get webhook subscriptions: {e}")
            return []
    
    def remove_webhook_subscription(self, tenant_id: str, webhook_id: str) -> bool:
        """Remove a webhook subscription."""
        if not self.cache.is_available():
            return False
        
        try:
            # Remove subscription
            webhook_key = f"webhook:{tenant_id}:{webhook_id}"
            self.cache.delete(webhook_key)
            
            # Update tenant's webhook list
            tenant_webhooks_key = f"webhooks:tenant:{tenant_id}"
            current_webhooks = self.cache.get(tenant_webhooks_key)
            
            if current_webhooks:
                webhook_list = json.loads(current_webhooks)
                if webhook_id in webhook_list:
                    webhook_list.remove(webhook_id)
                    self.cache.set(tenant_webhooks_key, json.dumps(webhook_list), ttl=86400 * 30)
            
            return True
            
        except Exception as e:
            print(f"Failed to remove webhook subscription: {e}")
            return False
    
    async def send_webhook_event(self, event: WebhookEvent) -> Dict[str, Any]:
        """Send webhook event to all subscribed endpoints."""
        if not self.session:
            await self._initialize_session()
        
        subscriptions = self.get_webhook_subscriptions(event.tenant_id)
        
        if not subscriptions:
            return {"sent": 0, "message": "No webhook subscriptions found"}
        
        # Filter subscriptions by event type
        relevant_subscriptions = [
            sub for sub in subscriptions 
            if sub.enabled and (event.event_type in sub.events or '*' in sub.events)
        ]
        
        if not relevant_subscriptions:
            return {"sent": 0, "message": "No subscriptions for this event type"}
        
        # Send webhooks concurrently
        delivery_tasks = []
        for subscription in relevant_subscriptions:
            task = self._deliver_webhook(event, subscription)
            delivery_tasks.append(task)
        
        results = await asyncio.gather(*delivery_tasks, return_exceptions=True)
        
        # Count successful deliveries
        successful = sum(1 for result in results if result is True)
        failed = len(results) - successful
        
        return {
            "sent": successful,
            "failed": failed,
            "total_subscriptions": len(relevant_subscriptions),
            "event_type": event.event_type
        }
    
    async def _deliver_webhook(self, event: WebhookEvent, subscription: WebhookSubscription) -> bool:
        """Deliver webhook to a single endpoint with retry logic."""
        payload = {
            "event_type": event.event_type,
            "timestamp": event.timestamp,
            "data": event.data,
            "tenant_id": event.tenant_id,
            "session_id": event.session_id,
            "webhook_id": subscription.webhook_id
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AI-Agent-Webhook/1.0"
        }
        
        # Add signature if secret is provided
        if subscription.secret:
            import hmac
            import hashlib
            
            signature = hmac.new(
                subscription.secret.encode(),
                json.dumps(payload).encode(),
                hashlib.sha256
            ).hexdigest()
            headers["X-Webhook-Signature"] = f"sha256={signature}"
        
        max_retries = subscription.retry_config.get("max_retries", 3)
        retry_delay = subscription.retry_config.get("retry_delay_seconds", 5)
        exponential_backoff = subscription.retry_config.get("exponential_backoff", True)
        
        for attempt in range(max_retries + 1):
            try:
                async with self.session.post(
                    subscription.url,
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status in [200, 201, 202, 204]:
                        return True
                    
                    print(f"Webhook delivery failed with status {response.status}")
                    
            except Exception as e:
                print(f"Webhook delivery error (attempt {attempt + 1}): {e}")
            
            # Wait before retry (except on last attempt)
            if attempt < max_retries:
                delay = retry_delay
                if exponential_backoff:
                    delay *= (2 ** attempt)
                await asyncio.sleep(delay)
        
        return False
    
    def get_webhook_stats(self, tenant_id: str) -> Dict[str, Any]:
        """Get webhook statistics for a tenant."""
        subscriptions = self.get_webhook_subscriptions(tenant_id)
        
        stats = {
            "total_webhooks": len(subscriptions),
            "enabled_webhooks": sum(1 for sub in subscriptions if sub.enabled),
            "event_types": set(),
            "webhook_urls": []
        }
        
        for subscription in subscriptions:
            stats["event_types"].update(subscription.events)
            stats["webhook_urls"].append({
                "webhook_id": subscription.webhook_id,
                "url": subscription.url,
                "enabled": subscription.enabled,
                "events": subscription.events
            })
        
        stats["event_types"] = list(stats["event_types"])
        
        return stats


# Global webhook manager instance
webhook_manager = WebhookManager()


# Common webhook events
async def send_message_processed_webhook(
    tenant_id: str,
    session_id: str,
    message: str,
    reply: str,
    tools_used: List[str],
    confidence: float
):
    """Send webhook for processed message."""
    event = WebhookEvent(
        event_type="message_processed",
        tenant_id=tenant_id,
        session_id=session_id,
        data={
            "message": message,
            "reply": reply,
            "tools_used": tools_used,
            "confidence": confidence
        }
    )
    
    return await webhook_manager.send_webhook_event(event)


async def send_error_webhook(
    tenant_id: str,
    error_type: str,
    error_message: str,
    context: Dict[str, Any]
):
    """Send webhook for error events."""
    event = WebhookEvent(
        event_type="error_occurred",
        tenant_id=tenant_id,
        data={
            "error_type": error_type,
            "error_message": error_message,
            "context": context
        }
    )
    
    return await webhook_manager.send_webhook_event(event)
