import os
import time
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    ListSortOrder,
    McpTool,
    RequiredMcpToolCall,
    SubmitToolApprovalAction,
    ToolApproval,
)
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor
from azure.ai.agents.telemetry import trace_function

load_dotenv()

# Enable Azure Monitor tracing
application_insights_connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
if application_insights_connection_string:
    configure_azure_monitor(connection_string=application_insights_connection_string)
    print("Azure Monitor tracing configured")
else:
    print("Warning: APPLICATIONINSIGHTS_CONNECTION_STRING not set - tracing disabled")

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)

@trace_function()
def get_or_create_agent(agent_name="PostgreSQL-MCP-Agent"):
    """Get existing agent by name or create new one if doesn't exist"""
    
    span = trace.get_current_span()
    span.set_attribute("agent_name", agent_name)
    
    mcp_server_url = os.environ.get("MCP_SERVER_URL")
    mcp_server_label = os.environ.get("MCP_SERVER_LABEL") 
    mcp_subscription_key = os.environ.get("MCP_SUBSCRIPTION_KEY")
    project_endpoint = os.environ.get("PROJECT_ENDPOINT")
    model_deployment = os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4o")
    
    span.set_attribute("model_deployment", model_deployment)
    span.set_attribute("mcp_server_label", mcp_server_label or "unknown")
    
    project_client = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(),
    )
    
    agents_client = project_client.agents
    
    # Check if agent already exists
    try:
        agents = list(agents_client.list_agents())
        print(f"Found {len(agents)} existing agents")
        for existing_agent in agents:
            print(f"Agent: {existing_agent.name} ({existing_agent.id})")
            if existing_agent.name == agent_name:
                print(f"Using existing agent: {existing_agent.id}")
                return existing_agent, project_client
    except Exception as e:
        print(f"Failed to list agents: {e}")
        pass
    
    # Create new agent
    mcp_tool = McpTool(
        server_label=mcp_server_label,
        server_url=mcp_server_url,
        allowed_tools=[],
    )
    
    if mcp_subscription_key:
        mcp_tool.update_headers("Ocp-Apim-Subscription-Key", mcp_subscription_key)
    
    agent = agents_client.create_agent(
        model=model_deployment,
        name=agent_name,
        instructions="You are a PostgreSQL database assistant that can query databases using MCP tools.",
        tools=mcp_tool.definitions,
    )
    
    print(f"Created new agent: {agent.id}")
    return agent, project_client

@trace_function()
def run_agent_query(agent, project_client, query):
    """Run a query using the agent"""
    
    span = trace.get_current_span()
    span.set_attribute("agent_id", agent.id)
    span.set_attribute("query", query)
    
    mcp_subscription_key = os.environ.get("MCP_SUBSCRIPTION_KEY")
    mcp_server_url = os.environ.get("MCP_SERVER_URL")
    mcp_server_label = os.environ.get("MCP_SERVER_LABEL")
    
    with project_client:
        agents_client = project_client.agents
        
        # Create MCP tool for runtime
        mcp_tool = McpTool(
            server_label=mcp_server_label,
            server_url=mcp_server_url,
            allowed_tools=[],
        )
        
        if mcp_subscription_key:
            mcp_tool.update_headers("Ocp-Apim-Subscription-Key", mcp_subscription_key)
        
        # Create thread and run
        thread = agents_client.threads.create()
        agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content=query,
        )
        
        run = agents_client.runs.create(
            thread_id=thread.id,
            agent_id=agent.id,
            tool_resources=mcp_tool.resources
        )
        
        # Handle tool calls
        with tracer.start_as_current_span("handle_tool_calls") as tool_span:
            tool_span.set_attribute("run_id", run.id)
            tool_span.set_attribute("thread_id", thread.id)
            
            while run.status in ["queued", "in_progress", "requires_action"]:
                time.sleep(1)
                run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)
                tool_span.set_attribute("run_status", run.status)
                
                if run.status == "requires_action" and isinstance(run.required_action, SubmitToolApprovalAction):
                    tool_calls = run.required_action.submit_tool_approval.tool_calls
                    tool_span.set_attribute("tool_calls_count", len(tool_calls) if tool_calls else 0)
                    
                    if not tool_calls:
                        agents_client.runs.cancel(thread_id=thread.id, run_id=run.id)
                        break
                    
                    tool_approvals = []
                    for tool_call in tool_calls:
                        if isinstance(tool_call, RequiredMcpToolCall):
                            tool_approvals.append(
                                ToolApproval(
                                    tool_call_id=tool_call.id,
                                    approve=True,
                                    headers=mcp_tool.headers,
                                )
                            )
                    
                    if tool_approvals:
                        agents_client.runs.submit_tool_outputs(
                            thread_id=thread.id, run_id=run.id, tool_approvals=tool_approvals
                        )
        
        # Get response
        with tracer.start_as_current_span("get_response") as response_span:
            messages = list(agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING))
            response_span.set_attribute("message_count", len(messages))
            
            for msg in messages:
                if msg.role == "assistant" and msg.text_messages:
                    response_text = msg.text_messages[-1].text.value
                    response_span.set_attribute("response_length", len(response_text))
                    return response_text
            
            return "No response from agent"

if __name__ == "__main__":
    with tracer.start_as_current_span("main_execution") as main_span:
        try:
            main_span.set_attribute("scenario", scenario)
            agent, project_client = get_or_create_agent()
            query = "Fetch me the sample records from users table in the fashion database"
            response = run_agent_query(agent, project_client, query)
            
            main_span.set_attribute("execution_status", "success")
            main_span.set_attribute("response_received", bool(response))
            
            print("\n" + "="*50)
            print("AGENT RESPONSE:")
            print("="*50)
            print(response)
            
        except Exception as e:
            main_span.set_attribute("execution_status", "error")
            main_span.set_attribute("error_message", str(e))
            print(f"Error: {e}")
            raise