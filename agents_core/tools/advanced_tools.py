"""Advanced business tools for the AI agent."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import RunContext
import json

from agents_core.orchestrator.agent import Deps


class EmailInput(BaseModel):
    """Input for sending emails."""
    to_email: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    message: str = Field(..., description="Email message content")
    priority: str = Field(default="normal", description="Email priority: low, normal, high")


class EmailOutput(BaseModel):
    """Output for email sending."""
    success: bool = Field(..., description="Whether email was sent successfully")
    message_id: str = Field(..., description="Email message ID")
    timestamp: str = Field(..., description="When email was sent")


class NotificationInput(BaseModel):
    """Input for sending notifications."""
    user_id: str = Field(..., description="User ID to notify")
    message: str = Field(..., description="Notification message")
    type: str = Field(default="info", description="Notification type: info, warning, error, success")
    channel: str = Field(default="app", description="Notification channel: app, sms, email")


class NotificationOutput(BaseModel):
    """Output for notifications."""
    success: bool = Field(..., description="Whether notification was sent")
    notification_id: str = Field(..., description="Notification ID")
    delivered_at: str = Field(..., description="Delivery timestamp")


class DocumentSearchInput(BaseModel):
    """Input for document search."""
    query: str = Field(..., description="Search query")
    document_type: str = Field(default="all", description="Type of documents to search")
    limit: int = Field(default=10, description="Maximum number of results")


class DocumentSearchOutput(BaseModel):
    """Output for document search."""
    results: List[Dict[str, Any]] = Field(..., description="Search results")
    total_found: int = Field(..., description="Total documents found")
    search_time_ms: int = Field(..., description="Search time in milliseconds")


class CalendarInput(BaseModel):
    """Input for calendar operations."""
    action: str = Field(..., description="Action: create, update, delete, search")
    event_details: Dict[str, Any] = Field(..., description="Event details")


class CalendarOutput(BaseModel):
    """Output for calendar operations."""
    success: bool = Field(..., description="Whether operation was successful")
    event_id: str = Field(..., description="Event ID")
    details: Dict[str, Any] = Field(..., description="Event details")


class PaymentInput(BaseModel):
    """Input for payment processing."""
    amount: float = Field(..., description="Payment amount")
    currency: str = Field(default="USD", description="Payment currency")
    customer_id: str = Field(..., description="Customer ID")
    description: str = Field(..., description="Payment description")


class PaymentOutput(BaseModel):
    """Output for payment processing."""
    success: bool = Field(..., description="Whether payment was processed")
    transaction_id: str = Field(..., description="Transaction ID")
    status: str = Field(..., description="Payment status")
    amount_charged: float = Field(..., description="Amount actually charged")


# Advanced tool implementations
async def send_email(input_data: EmailInput) -> EmailOutput:
    """Send an email to a customer or prospect."""
    await asyncio.sleep(0.1)  # Simulate API call
    
    # Mock email sending
    message_id = f"email_{datetime.now().timestamp()}"
    
    return EmailOutput(
        success=True,
        message_id=message_id,
        timestamp=datetime.now().isoformat()
    )


async def send_notification(input_data: NotificationInput) -> NotificationOutput:
    """Send a notification to a user."""
    await asyncio.sleep(0.1)  # Simulate API call
    
    # Mock notification sending
    notification_id = f"notif_{datetime.now().timestamp()}"
    
    return NotificationOutput(
        success=True,
        notification_id=notification_id,
        delivered_at=datetime.now().isoformat()
    )


async def search_documents(input_data: DocumentSearchInput) -> DocumentSearchOutput:
    """Search through company documents and knowledge base."""
    await asyncio.sleep(0.2)  # Simulate search
    
    # Mock document search results
    results = [
        {
            "title": f"Document about {input_data.query}",
            "summary": f"This document contains information related to {input_data.query}",
            "url": f"/documents/doc_{hash(input_data.query) % 1000}",
            "relevance_score": 0.95,
            "last_updated": "2024-01-15"
        },
        {
            "title": f"FAQ: {input_data.query}",
            "summary": f"Frequently asked questions about {input_data.query}",
            "url": f"/faq/faq_{hash(input_data.query) % 500}",
            "relevance_score": 0.87,
            "last_updated": "2024-01-10"
        }
    ]
    
    return DocumentSearchOutput(
        results=results[:input_data.limit],
        total_found=len(results),
        search_time_ms=156
    )


async def manage_calendar(input_data: CalendarInput) -> CalendarOutput:
    """Manage calendar events (create, update, delete, search)."""
    await asyncio.sleep(0.1)  # Simulate calendar API
    
    event_id = f"event_{datetime.now().timestamp()}"
    
    if input_data.action == "create":
        return CalendarOutput(
            success=True,
            event_id=event_id,
            details={
                "action": "created",
                "title": input_data.event_details.get("title", "New Event"),
                "start_time": input_data.event_details.get("start_time"),
                "duration": input_data.event_details.get("duration", "1 hour")
            }
        )
    elif input_data.action == "search":
        return CalendarOutput(
            success=True,
            event_id="search_results",
            details={
                "action": "search",
                "found_events": 3,
                "next_available": (datetime.now() + timedelta(hours=2)).isoformat()
            }
        )
    else:
        return CalendarOutput(
            success=True,
            event_id=event_id,
            details={"action": input_data.action, "status": "completed"}
        )


async def process_payment(input_data: PaymentInput) -> PaymentOutput:
    """Process a payment for services."""
    await asyncio.sleep(0.3)  # Simulate payment processing
    
    # Mock payment processing
    transaction_id = f"txn_{datetime.now().timestamp()}"
    
    # Simulate different outcomes
    if input_data.amount > 10000:
        return PaymentOutput(
            success=False,
            transaction_id=transaction_id,
            status="declined",
            amount_charged=0.0
        )
    
    return PaymentOutput(
        success=True,
        transaction_id=transaction_id,
        status="completed",
        amount_charged=input_data.amount
    )


def register_advanced_tools(agent_instance):
    """Register advanced tools with the agent."""
    
    if agent_instance is None:
        return
    
    try:
        # Email tool
        @agent_instance.tool
        async def send_email_tool(ctx: RunContext[Deps], input_data: EmailInput) -> EmailOutput:
            """Send an email to customers, prospects, or team members. Use this when the user asks to send an email or contact someone."""
            return await send_email(input_data)
        
        # Notification tool
        @agent_instance.tool
        async def send_notification_tool(ctx: RunContext[Deps], input_data: NotificationInput) -> NotificationOutput:
            """Send notifications to users via app, SMS, or email. Use this to notify users about important updates."""
            return await send_notification(input_data)
        
        # Document search tool
        @agent_instance.tool
        async def search_documents_tool(ctx: RunContext[Deps], input_data: DocumentSearchInput) -> DocumentSearchOutput:
            """Search through company documents, knowledge base, and FAQs. Use this when users ask for information that might be in documents."""
            return await search_documents(input_data)
        
        # Calendar management tool
        @agent_instance.tool
        async def manage_calendar_tool(ctx: RunContext[Deps], input_data: CalendarInput) -> CalendarOutput:
            """Manage calendar events - create, update, delete, or search for available times. Use this for scheduling and calendar operations."""
            return await manage_calendar(input_data)
        
        # Payment processing tool
        @agent_instance.tool
        async def process_payment_tool(ctx: RunContext[Deps], input_data: PaymentInput) -> PaymentOutput:
            """Process payments for services or products. Use this when users want to make payments or purchases."""
            return await process_payment(input_data)
        
        print("✅ Advanced tools registered successfully")
    except Exception as e:
        print(f"⚠️ Error registering advanced tools: {e}")
        # Continue anyway, don't fail agent creation


# Available advanced tools for API endpoint
ADVANCED_TOOLS = [
    {
        "name": "send_email",
        "description": "Send emails to customers, prospects, or team members",
        "input_schema": EmailInput.model_json_schema(),
        "category": "communication"
    },
    {
        "name": "send_notification", 
        "description": "Send notifications via app, SMS, or email",
        "input_schema": NotificationInput.model_json_schema(),
        "category": "communication"
    },
    {
        "name": "search_documents",
        "description": "Search company documents and knowledge base",
        "input_schema": DocumentSearchInput.model_json_schema(),
        "category": "information"
    },
    {
        "name": "manage_calendar",
        "description": "Manage calendar events and scheduling",
        "input_schema": CalendarInput.model_json_schema(),
        "category": "scheduling"
    },
    {
        "name": "process_payment",
        "description": "Process payments for services or products",
        "input_schema": PaymentInput.model_json_schema(),
        "category": "finance"
    }
]
