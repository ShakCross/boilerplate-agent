"""Main PydanticAI Agent orchestrator."""

import os
from typing import Dict, Any, List
from pydantic_ai import Agent, RunContext
from pydantic_ai.settings import ModelSettings
from pydantic import BaseModel

from agents_core.config.settings import settings, TenantConfig


class Deps(BaseModel):
    """Dependencies passed to the agent."""
    tenant: Dict[str, Any]
    session_summary: str = ""
    language: str = "en"
    session_id: str = ""


# Create the main agent (only if OpenAI key is available)
agent = None
agent_configured = False

def reset_agent():
    """Reset the agent to force recreation with new instructions."""
    global agent, agent_configured
    agent = None
    agent_configured = False

def get_agent():
    """Get or create the agent instance."""
    global agent, agent_configured
    if agent is None and settings.openai_api_key and settings.openai_api_key.strip():
        try:
            agent = Agent(
                model=f"openai:{settings.llm_model}",
                deps_type=Deps,
                instructions=(
                    "You are a helpful, professional AI assistant with access to comprehensive business tools. "
                    "You can help users with scheduling, communications, document search, payments, and general assistance. "
                    "\nIMPORTANT - TOOL USAGE:\n"
                    "- ALWAYS use the available tools when the user requests actions that match tool capabilities\n"
                    "- For scheduling visits: use the schedule_visit tool\n"
                    "- For business hours: use the get_business_hours tool\n"
                    "- For property information: use the get_property_info tool\n"
                    "- For sending emails: use the send_email_tool\n"
                    "- For notifications: use the send_notification_tool\n"
                    "- For document searches: use the search_documents_tool\n"
                    "- For calendar management: use the manage_calendar_tool\n"
                    "- For payments: use the process_payment_tool\n"
                    "- DO NOT provide direct answers for actions that have dedicated tools\n"
                    "\nGuidelines:\n"
                    "1. Be concise and helpful in your responses\n"
                    "2. Use the session context and summary when available\n"
                    "3. ALWAYS use appropriate tools when available for the task\n"
                    "4. Respect the tenant's tone and policies\n"
                    "5. Reply in the user's preferred language\n"
                    "6. When using tools, explain what you're doing\n"
                    "7. Keep responses professional but friendly\n"
                    "8. For complex requests, break them down and use multiple tools as needed\n"
                ),
                model_settings=ModelSettings(
                    temperature=settings.temperature,
                    max_tokens=settings.max_tokens
                ),
            )
            
            # Configure agent once
            if not agent_configured:
                setup_agent_prompts(agent)
                # Register tools
                try:
                    from agents_core.tools.business_tools import register_tools
                    from agents_core.tools.advanced_tools import register_advanced_tools
                    register_tools(agent)
                    register_advanced_tools(agent)
                except ImportError:
                    pass
                agent_configured = True
                
        except Exception as e:
            print(f"Warning: Could not initialize OpenAI agent: {e}")
            agent = None
    return agent


def setup_agent_prompts(agent_instance):
    """Setup system prompts for the agent."""
    @agent_instance.system_prompt
    async def system_prompt(ctx: RunContext[Deps]) -> str:
        """Dynamic system prompt based on tenant configuration."""
        deps = ctx.deps
        
        prompt_parts = [
            "You are a helpful AI assistant.",
            f"Session context: {deps.session_summary}" if deps.session_summary else "",
            f"Respond in {deps.language} language.",
        ]
        
        # Add tenant-specific instructions
        if deps.tenant:
            tone = deps.tenant.get('tone', 'professional')
            custom_instructions = deps.tenant.get('custom_instructions', '')
            disclaimers = deps.tenant.get('disclaimers', [])
            
            prompt_parts.extend([
                f"Use a {tone} tone.",
                custom_instructions,
                "Important disclaimers: " + "; ".join(disclaimers) if disclaimers else "",
            ])
        
        return "\n".join(filter(None, prompt_parts))


async def run_agent(
    message: str,
    session_id: str,
    tenant_config: TenantConfig,
    session_summary: str = "",
    language: str = "en",
    trace_id: str = None
) -> Dict[str, Any]:
    """
    Run the PydanticAI agent with the given message and context.
    
    Args:
        message: User message
        session_id: Session identifier
        tenant_config: Tenant configuration
        session_summary: Summary of previous conversation
        language: User's preferred language
        
    Returns:
        Dictionary with agent response and metadata
    """
    try:
        # Check if OpenAI API key is available
        if not settings.openai_api_key:
            return {
                "reply": "I'm sorry, but I'm not properly configured to process your request. Please contact support.",
                "session_id": session_id,
                "confidence": 0.0,
                "tools_used": [],
                "metadata": {
                    "error": "OpenAI API key not configured",
                    "model_used": settings.llm_model,
                    "tenant_id": tenant_config.tenant_id,
                    "locale": language
                }
            }
        
        # Prepare dependencies
        deps = Deps(
            tenant=tenant_config.to_dict(),
            session_summary=session_summary,
            language=language,
            session_id=session_id
        )
        
        # Get agent instance
        agent_instance = get_agent()
        if not agent_instance:
            return {
                "reply": "I'm sorry, but I'm not properly configured with AI capabilities. Please contact support.",
                "session_id": session_id,
                "confidence": 0.0,
                "tools_used": [],
                "metadata": {
                    "error": "Agent not initialized - OpenAI API key required",
                    "model_used": settings.llm_model,
                    "tenant_id": tenant_config.tenant_id,
                    "locale": language
                }
            }
        
        # Log to Langfuse if trace_id provided
        if trace_id:
            from agents_core.observability.langfuse_client import langfuse_client
            langfuse_client.log_generation(
                trace_id=trace_id,
                name="agent_generation",
                input_data={"message": message, "deps": deps.model_dump()},
                model=settings.llm_model,
                metadata={"session_id": session_id, "tenant_id": tenant_config.tenant_id}
            )
        
        # Run the agent (already configured in get_agent)
        result = await agent_instance.run(message, deps=deps)
        
        # Extract tools used (if any)
        tools_used = []
        if hasattr(result, 'all_messages'):
            for msg in result.all_messages():
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    tools_used.extend([call.function.name for call in msg.tool_calls])
        
        return {
            "reply": result.output,
            "session_id": session_id,
            "confidence": 0.95,  # We'll implement proper confidence scoring later
            "tools_used": tools_used,
            "metadata": {
                "model_used": settings.llm_model,
                "tenant_id": tenant_config.tenant_id,
                "locale": language,
                "tokens_used": getattr(result.usage, 'total_tokens', 0) if hasattr(result, 'usage') and result.usage else 0,
                "mock_response": False
            }
        }
        
    except Exception as e:
        # Fallback response in case of errors
        return {
            "reply": f"I apologize, but I encountered an issue processing your request. Please try again or contact support if the problem persists.",
            "session_id": session_id,
            "confidence": 0.0,
            "tools_used": [],
            "metadata": {
                "error": str(e),
                "model_used": settings.llm_model,
                "tenant_id": tenant_config.tenant_id,
                "locale": language,
                "mock_response": False
            }
        }


# Tools are imported and registered dynamically when the agent is used
