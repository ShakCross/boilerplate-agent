"""Business tools for the AI agent."""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from pydantic_ai import RunContext
from datetime import datetime
import uuid

from agents_core.orchestrator.agent import Deps


class ScheduleVisitInput(BaseModel):
    """Input schema for scheduling a visit."""
    property_id: str = Field(..., description="ID of the property to visit")
    datetime_iso: str = Field(..., description="Preferred date and time in ISO format")
    name: str = Field(..., description="Name of the person scheduling the visit")
    phone: str = Field(..., description="Contact phone number")
    email: str = Field(default="", description="Optional email address")


class ScheduleVisitOutput(BaseModel):
    """Output schema for scheduling a visit."""
    confirmation_id: str = Field(..., description="Unique confirmation ID")
    status: str = Field(..., description="Status of the scheduling request")
    message: str = Field(..., description="Human-readable confirmation message")
    scheduled_datetime: str = Field(..., description="Confirmed date and time")


class BusinessHoursOutput(BaseModel):
    """Output schema for business hours query."""
    hours: Dict[str, str] = Field(..., description="Business hours by day of week")
    timezone: str = Field(..., description="Timezone for the hours")
    special_notes: List[str] = Field(default_factory=list, description="Special notes about hours")


async def schedule_visit(ctx: RunContext[Deps], data: ScheduleVisitInput) -> ScheduleVisitOutput:
    """
    Schedule a property visit for a potential client.
    
    This tool allows users to schedule visits to properties by providing
    their contact information and preferred time.
    """
    try:
        # Generate a confirmation ID
        confirmation_id = f"VISIT-{uuid.uuid4().hex[:8].upper()}"
        
        # In a real implementation, this would:
        # 1. Check calendar availability
        # 2. Send notifications to property agents
        # 3. Create calendar entries
        # 4. Send confirmation emails
        
        # For now, we'll simulate the booking
        return ScheduleVisitOutput(
            confirmation_id=confirmation_id,
            status="confirmed",
            message=f"Visit confirmed for {data.name} on {data.datetime_iso}. You will receive a confirmation call at {data.phone}.",
            scheduled_datetime=data.datetime_iso
        )
        
    except Exception as e:
        return ScheduleVisitOutput(
            confirmation_id="",
            status="error",
            message=f"Unable to schedule visit: {str(e)}",
            scheduled_datetime=""
        )


async def get_business_hours(ctx: RunContext[Deps]) -> BusinessHoursOutput:
    """
    Get current business hours and availability information.
    
    This tool provides information about when the business is open
    and available for appointments or visits.
    """
    return BusinessHoursOutput(
        hours={
            "Monday": "9:00 AM - 6:00 PM",
            "Tuesday": "9:00 AM - 6:00 PM", 
            "Wednesday": "9:00 AM - 6:00 PM",
            "Thursday": "9:00 AM - 6:00 PM",
            "Friday": "9:00 AM - 5:00 PM",
            "Saturday": "10:00 AM - 3:00 PM",
            "Sunday": "Closed"
        },
        timezone="UTC-5 (Eastern Time)",
        special_notes=[
            "Appointments available outside business hours by request",
            "Holiday hours may vary",
            "Emergency support available 24/7"
        ]
    )


async def get_property_info(ctx: RunContext[Deps], property_id: str) -> Dict[str, Any]:
    """
    Get basic information about a property.
    
    Args:
        property_id: The ID of the property to look up
        
    Returns:
        Dictionary with property information
    """
    # In a real implementation, this would query a property database
    # For now, return mock data
    return {
        "property_id": property_id,
        "address": "123 Main Street, City, State 12345",
        "type": "Single Family Home",
        "bedrooms": 3,
        "bathrooms": 2,
        "square_feet": 1850,
        "price": "$350,000",
        "status": "Available",
        "description": "Beautiful 3-bedroom home with updated kitchen and spacious backyard.",
        "features": ["Updated Kitchen", "Hardwood Floors", "Fenced Yard", "Garage"]
    }


def register_tools(agent_instance):
    """Register business tools with the agent instance."""
    if agent_instance is None:
        return
    
    try:
        # Simple registration without conflict checking for now
        agent_instance.tool(schedule_visit)
        agent_instance.tool(get_business_hours)
        agent_instance.tool(get_property_info)
        print("✅ Business tools registered successfully")
    except Exception as e:
        print(f"⚠️ Error registering business tools: {e}")
        # Continue anyway, don't fail agent creation


# Tool metadata for the agent
AVAILABLE_TOOLS = [
    {
        "name": "schedule_visit",
        "description": "Schedule a property visit",
        "category": "scheduling",
        "parameters": ScheduleVisitInput
    },
    {
        "name": "get_business_hours", 
        "description": "Get business hours and availability",
        "category": "information",
        "parameters": None
    },
    {
        "name": "get_property_info",
        "description": "Get information about a specific property",
        "category": "information",
        "parameters": {"property_id": "string"}
    }
]
