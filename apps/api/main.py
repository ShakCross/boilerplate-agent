"""Main FastAPI application - UPDATED VERSION."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents_core.config.settings import settings
from agents_core.schemas.message import MessageDTO, AgentResponse


# Create FastAPI app
app = FastAPI(
    title="AI Agent API - Updated",
    description="AI Agent Boilerplate using FastAPI + PydanticAI + OpenAI - UPDATED VERSION",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    print(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Agent API is running - UPDATED VERSION!",
        "version": "0.2.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "updated",
        "model": settings.llm_model,
        "max_tokens": settings.max_tokens,
        "temperature": settings.temperature
    }


@app.post("/message", response_model=AgentResponse)
async def process_message(message_dto: MessageDTO, request: Request):
    """
    Process a chat message and return AI response using PydanticAI agent.
    UPDATED VERSION with Langfuse observability and rate limiting.
    """
    from agents_core.observability.langfuse_client import langfuse_client
    from agents_core.middleware.rate_limiting import apply_rate_limit
    
    # Apply rate limiting (60 requests per minute per session)
    rate_limit_key = f"session:{message_dto.session_id}"
    rate_metadata = apply_rate_limit(
        identifier=rate_limit_key,
        limit=60,
        window=60,
        error_message="Too many messages. Please wait before sending another."
    )
    
    # Create Langfuse trace for observability
    trace = langfuse_client.create_trace(
        name="chat_message",
        session_id=message_dto.session_id,
        metadata={
            "tenant_id": message_dto.tenant_id,
            "locale": message_dto.locale,
            "endpoint": "/message"
        }
    )
    
    try:
        print(f"[UPDATED ENDPOINT] Processing message: {message_dto.text}")
        
        # Apply input guardrails
        from agents_core.guardrails.input_validation import input_guardrails, output_guardrails
        
        is_valid, filtered_text, input_metadata = input_guardrails.validate_input(
            message_dto.text,
            message_dto.session_id
        )
        
        if not is_valid:
            print(f"[GUARDRAILS] Input rejected: {input_metadata.get('flags', [])}")
            
            # Log to Langfuse
            if trace:
                langfuse_client.client.create_event(
                    name="input_validation_failed",
                    input={"original_message": message_dto.text, "validation": input_metadata},
                    output={"error": "Input validation failed", "flags": input_metadata.get('flags', [])},
                    metadata={
                        "guardrails_triggered": True,
                        "trace_id": trace
                    }
                )
                langfuse_client.flush()
            
            raise HTTPException(
                status_code=400,
                detail="Your message contains content that cannot be processed. Please rephrase and try again."
            )
        
        print(f"[GUARDRAILS] Input validated successfully")
        
        # Import the agent and tools
        from agents_core.orchestrator.agent import run_agent
        from agents_core.config.settings import get_tenant_config
        
        print("[UPDATED ENDPOINT] Imported agent functions successfully")
        
        # Get tenant configuration
        tenant_config = get_tenant_config(message_dto.tenant_id)
        print(f"[UPDATED ENDPOINT] Got tenant config for {tenant_config.tenant_id}")
        
        # Get conversation memory
        from agents_core.memory.conversation_memory import conversation_memory
        
        # Get session context
        session_summary = conversation_memory.generate_context_summary(
            message_dto.session_id, 
            message_dto.tenant_id
        )
        
        print(f"[UPDATED ENDPOINT] Session summary: {session_summary[:100] if session_summary else 'No history'}")
        
        # Log input to Langfuse
        if trace:
            langfuse_client.client.create_event(
                name="message_input",
                input={
                    "message": message_dto.text,
                    "session_id": message_dto.session_id,
                    "tenant_id": message_dto.tenant_id,
                    "locale": message_dto.locale,
                    "session_summary": session_summary
                },
                metadata={"trace_id": trace}
            )
        
        # Run the AI agent with filtered input
        agent_result = await run_agent(
            message=filtered_text,  # Use filtered text instead of original
            session_id=message_dto.session_id,
            tenant_config=tenant_config,
            session_summary=session_summary,
            language=message_dto.locale,
            trace_id=trace if trace else None
        )
        
        print(f"[UPDATED ENDPOINT] Agent result: {agent_result['reply'][:50]}...")
        
        # Apply output guardrails
        output_valid, filtered_reply, output_metadata = output_guardrails.validate_output(
            agent_result["reply"],
            agent_result["confidence"],
            agent_result["tools_used"],
            agent_result["metadata"]
        )
        
        print(f"[GUARDRAILS] Output validated: {output_valid}")
        
        # Convert agent result to API response
        response = AgentResponse(
            reply=filtered_reply,  # Use filtered reply
            session_id=agent_result["session_id"],
            confidence=agent_result["confidence"],
            tools_used=agent_result["tools_used"],
            metadata={
                **agent_result["metadata"],
                "input_guardrails": input_metadata,
                "output_guardrails": output_metadata,
                "rate_limit": rate_metadata
            }
        )
        
        # Log output to Langfuse
        if trace:
            langfuse_client.client.create_event(
                name="message_output",
                output={
                    "reply": response.reply,
                    "confidence": response.confidence,
                    "tools_used": response.tools_used,
                    "success": True
                },
                metadata={
                    "tokens_used": agent_result["metadata"].get("tokens_used", 0),
                    "model_used": agent_result["metadata"].get("model_used", ""),
                    "response_length": len(response.reply),
                    "trace_id": trace
                }
            )
        
        # Save conversation to memory
        conversation_memory.add_message(
            session_id=message_dto.session_id,
            tenant_id=message_dto.tenant_id,
            role="user",
            content=message_dto.text,
            metadata={"locale": message_dto.locale}
        )
        
        conversation_memory.add_message(
            session_id=message_dto.session_id,
            tenant_id=message_dto.tenant_id,
            role="assistant",
            content=response.reply,
            metadata={
                "confidence": response.confidence,
                "tools_used": response.tools_used,
                "model": agent_result["metadata"].get("model_used", "")
            }
        )
        
        print(f"[UPDATED ENDPOINT] Returning response with confidence: {response.confidence}")
        
        # Send webhook notification (async, don't wait)
        try:
            from agents_core.webhooks.webhook_manager import send_message_processed_webhook
            asyncio.create_task(send_message_processed_webhook(
                tenant_id=message_dto.tenant_id,
                session_id=message_dto.session_id,
                message=filtered_text,
                reply=response.reply,
                tools_used=response.tools_used,
                confidence=response.confidence
            ))
        except Exception as e:
            print(f"Webhook notification failed: {e}")
        
        return response
        
    except Exception as e:
        print(f"[UPDATED ENDPOINT] Error in process_message: {str(e)}")
        
        # Log error to Langfuse
        if trace:
            langfuse_client.client.create_event(
                name="message_error",
                output={"error": str(e), "success": False},
                metadata={
                    "error_type": type(e).__name__,
                    "trace_id": trace
                }
            )
        
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )
    finally:
        # Ensure Langfuse events are sent
        langfuse_client.flush()


@app.get("/config/{tenant_id}")
async def get_tenant_config(tenant_id: str):
    """Get tenant configuration."""
    from agents_core.config.settings import get_tenant_config
    
    try:
        config = get_tenant_config(tenant_id)
        return config.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Tenant configuration not found: {str(e)}"
        )


@app.get("/metrics/system")
async def get_system_metrics():
    """Get system metrics and health information."""
    from agents_core.observability.langfuse_client import langfuse_client
    from agents_core.memory.conversation_memory import conversation_memory
    from agents_core.orchestrator.agent import get_agent
    
    metrics = {
        "system_status": "healthy",
        "components": {
            "openai_agent": get_agent() is not None,
            "langfuse": langfuse_client.is_available(),
            "redis_memory": conversation_memory.is_available(),
            "guardrails": True
        },
        "configuration": {
            "model": settings.llm_model,
            "max_tokens": settings.max_tokens,
            "temperature": settings.temperature,
            "debug_mode": settings.debug
        },
        "features": {
            "conversation_memory": conversation_memory.is_available(),
            "observability": langfuse_client.is_available(),
            "multi_tenant": True,
            "input_guardrails": True,
            "output_guardrails": True,
            "business_tools": True
        }
    }
    
    return metrics


@app.get("/tools/available")
async def get_available_tools():
    """Get list of available business tools."""
    try:
        from agents_core.tools.business_tools import AVAILABLE_TOOLS
        from agents_core.tools.advanced_tools import ADVANCED_TOOLS
        
        # Prepare tools with safe serialization
        def prepare_tool(tool):
            safe_tool = {
                "name": tool["name"],
                "description": tool["description"],
                "category": tool.get("category", "general")
            }
            # Only include parameters if they're serializable
            if tool.get("parameters") and not hasattr(tool["parameters"], "model_json_schema"):
                safe_tool["parameters"] = tool["parameters"]
            return safe_tool
        
        safe_basic_tools = [prepare_tool(tool) for tool in AVAILABLE_TOOLS]
        safe_advanced_tools = [prepare_tool(tool) for tool in ADVANCED_TOOLS]
        
        all_tools = safe_basic_tools + safe_advanced_tools
        categories = set()
        for tool in all_tools:
            categories.add(tool["category"])
        
        return {
            "basic_tools": safe_basic_tools,
            "advanced_tools": safe_advanced_tools,
            "all_tools": all_tools,
            "total_count": len(all_tools),
            "categories": list(categories)
        }
        
    except Exception as e:
        # Fallback response if there are issues with tools
        return {
            "basic_tools": [],
            "advanced_tools": [],
            "all_tools": [],
            "total_count": 0,
            "categories": [],
            "error": str(e),
            "message": "Error loading tools metadata"
        }


@app.get("/celery/status")
async def get_celery_status():
    """Get Celery worker status and statistics."""
    try:
        from workers.celery_worker.app import app as celery_app
        import redis
        
        # Test basic Redis connectivity first
        redis_url = settings.get_redis_url_for_memory()
        redis_client = redis.from_url(redis_url, socket_connect_timeout=2)
        redis_client.ping()
        
        # Get inspect instance with timeout
        inspect = celery_app.control.inspect(timeout=3.0)
        
        # Get worker statistics with error handling
        try:
            stats = inspect.stats()
            active_tasks = inspect.active()
            registered_tasks = inspect.registered()
        except Exception as inspect_error:
            # If inspection fails, try a different approach
            return {
                "status": "redis_connected_workers_unreachable",
                "redis_connected": True,
                "workers_online": "unknown",
                "message": f"Redis is connected but worker inspection failed: {str(inspect_error)}",
                "note": "Workers may be running in different network context (Docker)",
                "suggestion": "Check docker-compose logs worker"
            }
        
        if not stats:
            return {
                "status": "no_workers_detected",
                "redis_connected": True,
                "workers_online": 0,
                "message": "Redis is connected but no Celery workers detected via inspection",
                "note": "Workers may be running but not reachable for inspection"
            }
        
        return {
            "status": "healthy",
            "redis_connected": True,
            "workers_online": len(stats),
            "workers": list(stats.keys()) if stats else [],
            "active_tasks": len(active_tasks.get(list(stats.keys())[0], [])) if active_tasks and stats else 0,
            "registered_tasks": registered_tasks.get(list(stats.keys())[0], []) if registered_tasks and stats else [],
            "worker_stats": stats
        }
        
    except redis.ConnectionError as e:
        return {
            "status": "redis_connection_failed",
            "redis_connected": False,
            "error": str(e),
            "message": "Cannot connect to Redis"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to get Celery status"
        }


@app.post("/celery/test")
async def test_celery_task():
    """Test Celery by running a simple cleanup task."""
    try:
        from workers.celery_worker.tasks import cleanup_old_sessions
        
        # Submit task
        result = cleanup_old_sessions.delay()
        
        return {
            "success": True,
            "task_id": result.id,
            "message": "Task submitted successfully to Celery queue",
            "note": "Check worker logs to see task execution"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to submit task to Celery"
        }


@app.post("/message/async")
async def process_message_async_endpoint(message_dto: MessageDTO):
    """Process message asynchronously using Celery."""
    try:
        from workers.celery_worker.tasks import process_message_async
        
        # Prepare message data for Celery
        message_data = {
            "message": message_dto.text,
            "session_id": message_dto.session_id,
            "tenant_id": message_dto.tenant_id,
            "locale": message_dto.locale
        }
        
        # Submit to Celery
        result = process_message_async.delay(message_data)
        
        return {
            "task_id": result.id,
            "status": "submitted",
            "message": "Message submitted for async processing",
            "check_status_url": f"/celery/task/{result.id}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit async task: {str(e)}"
        )


@app.get("/celery/task/{task_id}")
async def get_celery_task_status(task_id: str):
    """Get the status of a Celery task by ID."""
    try:
        from workers.celery_worker.app import app as celery_app
        from celery.result import AsyncResult
        
        # Get task result
        result = AsyncResult(task_id, app=celery_app)
        
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
            "successful": result.successful() if result.ready() else None,
            "failed": result.failed() if result.ready() else None,
            "traceback": str(result.traceback) if result.failed() else None,
            "ready": result.ready(),
            "info": result.info
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task status: {str(e)}"
        )


@app.post("/celery/process-direct")
async def process_celery_task_directly():
    """Process a Celery task directly (for testing when workers aren't accessible)."""
    try:
        from workers.celery_worker.tasks import cleanup_old_sessions
        
        # Execute task directly instead of queueing
        result = cleanup_old_sessions()
        
        return {
            "success": True,
            "result": result,
            "message": "Task executed directly (not via Celery queue)",
            "note": "This bypasses Celery for testing purposes"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Direct task execution failed"
        }


@app.get("/celery/queue-status")
async def get_queue_status():
    """Get current queue status and statistics."""
    try:
        import redis
        
        redis_url = settings.get_redis_url_for_memory()
        redis_client = redis.from_url(redis_url)
        
        # Get queue information
        queue_info = {
            "agent_tasks_queue": redis_client.llen("agent_tasks"),
            "default_queue": redis_client.llen("celery"),
            "total_redis_keys": len(redis_client.keys("*")),
            "celery_keys": len(redis_client.keys("celery*")),
        }
        
        # Try to peek at queue content (first few items)
        queue_items = redis_client.lrange("agent_tasks", 0, 2)
        
        return {
            "queue_info": queue_info,
            "redis_url": redis_url,
            "sample_tasks": len(queue_items),
            "status": "connected"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to get queue status"
        }


@app.get("/monitoring/errors")
async def get_error_monitoring():
    """Get error monitoring statistics."""
    from agents_core.monitoring.error_tracking import error_tracker
    
    try:
        stats = error_tracker.get_error_stats()
        recent_errors = error_tracker.get_recent_errors(10)
        
        return {
            "status": "available",
            "statistics": stats,
            "recent_errors": recent_errors,
            "cache_available": error_tracker.cache.is_available()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to get error monitoring data"
        }


@app.get("/monitoring/performance/{endpoint}")
async def get_performance_stats(endpoint: str):
    """Get performance statistics for a specific endpoint."""
    from agents_core.monitoring.error_tracking import performance_monitor
    
    try:
        stats = performance_monitor.get_performance_stats(endpoint)
        return stats
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Failed to get performance stats for {endpoint}"
        }


@app.get("/monitoring/health")
async def comprehensive_health_check():
    """Comprehensive health check with all system components."""
    from agents_core.observability.langfuse_client import langfuse_client
    from agents_core.memory.conversation_memory import conversation_memory
    from agents_core.orchestrator.agent import get_agent
    from agents_core.middleware.rate_limiting import rate_limiter, cache_manager
    from agents_core.monitoring.error_tracking import error_tracker
    
    health_data = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "healthy",
        "components": {
            "openai_agent": {
                "status": "healthy" if get_agent() is not None else "unavailable",
                "details": "AI agent initialized and ready"
            },
            "langfuse": {
                "status": "healthy" if langfuse_client.is_available() else "unavailable",
                "details": "Observability and tracing system"
            },
            "redis_memory": {
                "status": "healthy" if conversation_memory.is_available() else "unavailable",
                "details": "Conversation memory and session storage"
            },
            "rate_limiter": {
                "status": "healthy" if rate_limiter.is_available() else "unavailable",
                "details": "API rate limiting protection"
            },
            "cache_manager": {
                "status": "healthy" if cache_manager.is_available() else "unavailable",
                "details": "Response caching and performance optimization"
            },
            "error_tracking": {
                "status": "healthy" if error_tracker.cache.is_available() else "limited",
                "details": "Error monitoring and tracking system"
            }
        },
        "configuration": {
            "model": settings.llm_model,
            "max_tokens": settings.max_tokens,
            "temperature": settings.temperature,
            "environment": settings.environment,
            "debug_mode": settings.debug
        }
    }
    
    # Check if any critical components are down
    critical_components = ["openai_agent", "redis_memory"]
    for component in critical_components:
        if health_data["components"][component]["status"] != "healthy":
            health_data["overall_status"] = "degraded"
            break
    
    # Add error statistics
    try:
        error_stats = error_tracker.get_error_stats()
        health_data["error_summary"] = {
            "last_24h_errors": error_stats.get("last_24h", 0),
            "error_rate_per_hour": error_stats.get("error_rate", 0),
            "critical_errors": error_stats.get("by_severity", {}).get("critical", 0)
        }
        
        # Mark as degraded if high error rate
        if error_stats.get("error_rate", 0) > 10:  # More than 10 errors per hour
            health_data["overall_status"] = "degraded"
            
    except Exception as e:
        health_data["error_summary"] = {"error": str(e)}
    
    return health_data


@app.post("/webhooks/subscribe")
async def subscribe_webhook(request: Request):
    """Subscribe to webhook events."""
    from agents_core.webhooks.webhook_manager import webhook_manager, WebhookSubscription
    
    try:
        webhook_data = await request.json()
        subscription = WebhookSubscription(**webhook_data)
        
        success = webhook_manager.add_webhook_subscription(subscription)
        
        if success:
            return {
                "success": True,
                "webhook_id": subscription.webhook_id,
                "message": "Webhook subscription created successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to create webhook subscription"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid webhook subscription data: {str(e)}"
        )


@app.get("/webhooks/{tenant_id}")
async def get_webhook_subscriptions(tenant_id: str):
    """Get all webhook subscriptions for a tenant."""
    from agents_core.webhooks.webhook_manager import webhook_manager
    
    try:
        subscriptions = webhook_manager.get_webhook_subscriptions(tenant_id)
        stats = webhook_manager.get_webhook_stats(tenant_id)
        
        return {
            "tenant_id": tenant_id,
            "subscriptions": [sub.model_dump() for sub in subscriptions],
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get webhook subscriptions: {str(e)}"
        )


@app.delete("/webhooks/{tenant_id}/{webhook_id}")
async def remove_webhook_subscription(tenant_id: str, webhook_id: str):
    """Remove a webhook subscription."""
    from agents_core.webhooks.webhook_manager import webhook_manager
    
    try:
        success = webhook_manager.remove_webhook_subscription(tenant_id, webhook_id)
        
        if success:
            return {
                "success": True,
                "message": f"Webhook {webhook_id} removed successfully"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="Webhook subscription not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to remove webhook subscription: {str(e)}"
        )


@app.post("/webhooks/test")
async def test_webhook_delivery():
    """Test webhook delivery with a sample event."""
    from agents_core.webhooks.webhook_manager import webhook_manager, WebhookEvent
    
    try:
        # Create test event
        test_event = WebhookEvent(
            event_type="test_event",
            tenant_id="test_tenant",
            session_id="test_session",
            data={
                "message": "This is a test webhook event",
                "test": True,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        result = await webhook_manager.send_webhook_event(test_event)
        
        return {
            "success": True,
            "delivery_result": result,
            "test_event": test_event.model_dump()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test webhook delivery: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
