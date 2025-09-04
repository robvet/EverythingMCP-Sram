import asyncio
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent
from azure.ai.agents.models import McpTool

load_dotenv()

async def invoke_existing_agent(agent_id, query):
    """Invoke an existing Azure AI agent using Semantic Kernel"""
    
    project_endpoint = os.environ.get("PROJECT_ENDPOINT")
    
    mcp_subscription_key = os.environ.get("MCP_SUBSCRIPTION_KEY")
    
    creds = DefaultAzureCredential()
    async with AzureAIAgent.create_client(
        endpoint=project_endpoint,
        credential=creds
    ) as client:
        # Get the existing agent definition
        print(f"Retrieving agent: {agent_id}")
        existing_agent_definition = await client.agents.get_agent(agent_id=agent_id)
        print(f"Agent found: {existing_agent_definition.name}")
                
        # Create MCP tool with headers for runtime
        mcp_tool = McpTool(
            server_label=os.environ.get("MCP_SERVER_LABEL"),
            server_url=os.environ.get("MCP_SERVER_URL"),
            allowed_tools=[],
        )
        
        if mcp_subscription_key:
            mcp_tool.update_headers("Ocp-Apim-Subscription-Key", mcp_subscription_key)
        

        
        # Create Semantic Kernel agent using modified definition
        agent = AzureAIAgent(
            client=client,
            definition=existing_agent_definition
        )
        
        # Try to pass tool resources to the invoke method
        print(f"Sending query: {query}")
        print("\nAgent Response:")
        print("=" * 50)
        
        # Check if we can access the underlying client to manually handle tool calls
        
        # Try to access the underlying client and manually create runs with tool resources
        try:
            
            # Access the underlying Azure AI client
            azure_client = agent.client
            
            # Create thread manually
            thread = await azure_client.agents.threads.create()
            print(f"Created thread: {thread.id}")
            
            # Add message
            await azure_client.agents.messages.create(
                thread_id=thread.id,
                role="user", 
                content=query
            )
            
            # Create run with tool resources
            run = await azure_client.agents.runs.create(
                thread_id=thread.id,
                agent_id=agent.id,
                tool_resources=mcp_tool.resources
            )
            print(f"Created run with tool resources: {run.id}")
            
            # Poll for completion with tool approval handling
            import asyncio
            from azure.ai.agents.models import SubmitToolApprovalAction, RequiredMcpToolCall, ToolApproval
            
            for _ in range(30):  # max 30 seconds
                await asyncio.sleep(1)
                run = await azure_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
                print(f"Run status: {run.status}")
                
                # Handle tool approvals - copy from main.py logic
                if run.status == "requires_action" and isinstance(run.required_action, SubmitToolApprovalAction):
                    tool_calls = run.required_action.submit_tool_approval.tool_calls
                    
                    if not tool_calls:
                        print("No tool calls - cancelling run")
                        await azure_client.agents.runs.cancel(thread_id=thread.id, run_id=run.id)
                        break
                    
                    tool_approvals = []
                    for tool_call in tool_calls:
                        if isinstance(tool_call, RequiredMcpToolCall):
                            print(f"Approving MCP tool call: {getattr(tool_call, 'name', getattr(tool_call, 'id', 'unknown'))}")
                            tool_approvals.append(
                                ToolApproval(
                                    tool_call_id=tool_call.id,
                                    approve=True,
                                    headers=mcp_tool.headers,
                                )
                            )
                    
                    if tool_approvals:
                        print(f"Submitting {len(tool_approvals)} tool approvals...")
                        await azure_client.agents.runs.submit_tool_outputs(
                            thread_id=thread.id, 
                            run_id=run.id, 
                            tool_approvals=tool_approvals
                        )
                
                elif run.status not in ["queued", "in_progress", "requires_action"]:
                    break
            
            print(f"Final run status: {run.status}")
            
            # Get messages
            messages_list = azure_client.agents.messages.list(thread_id=thread.id)
            async for msg in messages_list:
                if msg.role == "assistant" and msg.text_messages:
                    print(f"Assistant: {msg.text_messages[-1].text.value}")
            
        except Exception as e:
            print(f"Manual run approach failed: {e}")
            
            # Fallback: standard invoke
            async for response in agent.invoke(messages=query):
                print(response)

async def main():
    """Main function to test semantic kernel integration"""
    
    # Use the existing PostgreSQL MCP agent
    agent_id = "asst_RJv7MiFdKp9QYxwZOPFvhSqW"  # From our main.py output
    query = "Show me the users table data from the fashion database"
    
    try:
        await invoke_existing_agent(agent_id, query)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())