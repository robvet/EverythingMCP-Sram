"""
Semantic Kernel Plugin wrapper for Copilot Studio Agent
Uses our working copilot_studio_orchestrator as a plugin in Semantic Kernel
"""

import asyncio
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIChatCompletion
from copilot_studio_orchestrator import AutomatedCopilotStudioAgent


class CopilotStudioPlugin:
    """Semantic Kernel plugin that wraps our working Copilot Studio agent"""
    
    def __init__(self):
        self.copilot_agent = None
        self._initialized = False
    
    async def _ensure_initialized(self):
        """Ensure the Copilot Studio agent is initialized"""
        if not self._initialized:
            self.copilot_agent = AutomatedCopilotStudioAgent()
            await self.copilot_agent.initialize()
            self._initialized = True
    
    @kernel_function(
        description="Send a message to the Copilot Studio fashion database agent",
        name="ask_copilot_studio"
    )
    async def ask_copilot_studio(self, message: str) -> str:
        """Send a message to Copilot Studio agent and return the response"""
        await self._ensure_initialized()
        response = await self.copilot_agent.send_message(message)
        return response
    
    @kernel_function(
        description="Get information about fashion trends, clothing, or database queries",
        name="get_fashion_info"
    )
    async def get_fashion_info(self, query: str) -> str:
        """Specialized function for fashion-related queries"""
        await self._ensure_initialized()
        
        # Add context to the query for better results
        enhanced_query = f"Fashion database query: {query}"
        response = await self.copilot_agent.send_message(enhanced_query)
        return response


class SemanticKernelOrchestrator:
    """Semantic Kernel orchestrator using Copilot Studio as a plugin"""
    
    def __init__(self, use_openai: bool = False):
        self.kernel = Kernel()
        self.copilot_plugin = CopilotStudioPlugin()
        
        # Add the Copilot Studio plugin to the kernel
        self.kernel.add_plugin(self.copilot_plugin, plugin_name="copilot_studio")
        
        # Optionally add AI service for enhanced orchestration
        if use_openai:
            self._setup_ai_service()
    
    def _setup_ai_service(self):
        """Setup AI service for enhanced orchestration (optional)"""
        # This would require OpenAI/Azure OpenAI credentials
        # Uncomment and configure if needed
        pass
        # service_id = "chat-gpt"
        # self.kernel.add_service(OpenAIChatCompletion(
        #     service_id=service_id,
        #     ai_model_id="gpt-3.5-turbo",
        #     api_key="your-openai-key"
        # ))
    
    async def ask_question(self, question: str) -> str:
        """Ask a question using the Copilot Studio plugin"""
        try:
            # Get the function from the plugin
            ask_function = self.kernel.get_function("copilot_studio", "ask_copilot_studio")
            
            # Execute the function
            result = await ask_function.invoke(self.kernel, message=question)
            
            return str(result.value) if result.value else "No response received"
            
        except Exception as e:
            return f"Error: {e}"
    
    async def get_fashion_info(self, query: str) -> str:
        """Get fashion information using the specialized plugin function"""
        try:
            # Get the specialized fashion function
            fashion_function = self.kernel.get_function("copilot_studio", "get_fashion_info")
            
            # Execute the function
            result = await fashion_function.invoke(self.kernel, query=query)
            
            return str(result.value) if result.value else "No response received"
            
        except Exception as e:
            return f"Error: {e}"
    
    async def _show_thinking(self):
        """Show animated thinking dots"""
        try:
            while True:
                for i in range(4):
                    dots = "." * i
                    print(f"\r🤖 Semantic Kernel: Thinking{dots}   ", end="", flush=True)
                    await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            pass
    
    async def interactive_session(self):
        """Run an interactive session using Semantic Kernel orchestration"""
        print("🧠 Semantic Kernel + Copilot Studio Fashion Assistant")
        print("Powered by Semantic Kernel orchestration with Copilot Studio plugin")
        print("Type 'quit', 'exit', or 'q' to end the session")
        print("Type 'fashion:' before your query for specialized fashion queries")
        print("=" * 70)
        
        max_retries = 3
        retry_count = 0
        
        while True:
            try:
                try:
                    user_input = input("\n👤 You: ")
                except EOFError:
                    print("\n👋 Goodbye!")
                    break
                    
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break
                
                if not user_input.strip():
                    continue
                
                # Rate limiting
                if retry_count > 0:
                    await asyncio.sleep(min(2**retry_count, 10))
                
                print("🧠 Semantic Kernel: Thinking", end="", flush=True)
                
                # Show thinking animation
                thinking_task = asyncio.create_task(self._show_thinking())
                
                try:
                    # Check if it's a fashion-specific query
                    if user_input.lower().startswith("fashion:"):
                        query = user_input[8:].strip()  # Remove "fashion:" prefix
                        response = await asyncio.wait_for(
                            self.get_fashion_info(query), 
                            timeout=120.0
                        )
                    else:
                        # Use general ask function
                        response = await asyncio.wait_for(
                            self.ask_question(user_input), 
                            timeout=120.0
                        )
                    
                    thinking_task.cancel()
                    print(f"\r🧠 Semantic Kernel → 🤖 Copilot Studio: {response}")
                    retry_count = 0
                    
                except asyncio.TimeoutError:
                    thinking_task.cancel()
                    print("\r❌ Request timed out. Please try again.")
                    retry_count += 1
                    if retry_count >= max_retries:
                        print(f"❌ Maximum retries ({max_retries}) reached. Exiting.")
                        break
                        
                except Exception as e:
                    thinking_task.cancel()
                    print(f"\r❌ Error: {e}")
                    retry_count += 1
                    if retry_count >= max_retries:
                        print(f"❌ Maximum retries ({max_retries}) reached. Exiting.")
                        break
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                retry_count += 1
                if retry_count >= max_retries:
                    print(f"❌ Maximum retries ({max_retries}) reached. Exiting.")
                    break
    
    async def demo_kernel_features(self):
        """Demonstrate Semantic Kernel features with our plugin"""
        print("🧠 Semantic Kernel Plugin Demo")
        print("=" * 40)
        
        # List available plugins
        print("\n📋 Available Plugins:")
        for plugin_name in self.kernel.plugins.keys():
            print(f"  - {plugin_name}")
            plugin = self.kernel.plugins[plugin_name]
            for function_name in plugin.functions.keys():
                print(f"    └── {function_name}")
        
        # Demo questions
        demo_questions = [
            "Hello, what can you help me with?",
            "fashion: What are the latest sustainable fashion trends?",
            "Can you tell me about your database capabilities?"
        ]
        
        print(f"\n🎯 Running {len(demo_questions)} demo queries:")
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n[{i}] Demo Query: {question}")
            print("🧠 Processing", end="", flush=True)
            
            thinking_task = asyncio.create_task(self._show_thinking())
            
            try:
                if question.startswith("fashion:"):
                    query = question[8:].strip()
                    response = await self.get_fashion_info(query)
                else:
                    response = await self.ask_question(question)
                
                thinking_task.cancel()
                print(f"\r🧠 Response: {response}")
                
            except Exception as e:
                thinking_task.cancel()
                print(f"\r❌ Error: {e}")
            
            await asyncio.sleep(1)  # Brief pause between demos


async def main():
    """Main function demonstrating Semantic Kernel orchestration"""
    try:
        print("🚀 Initializing Semantic Kernel Orchestrator...")
        orchestrator = SemanticKernelOrchestrator(use_openai=False)
        
        print("\nSelect mode:")
        print("1. Interactive session")
        print("2. Demo kernel features")
        
        try:
            choice = input("Enter choice (1 or 2): ").strip()
        except EOFError:
            choice = "1"
        
        if choice == "2":
            await orchestrator.demo_kernel_features()
        else:
            await orchestrator.interactive_session()
            
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Application terminated")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")