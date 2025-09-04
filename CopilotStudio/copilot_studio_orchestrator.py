"""
Copilot Studio Agent implementation using microsoft_agents libraries
Based on .env configuration for automated agent interaction
"""

import asyncio
import os
from dotenv import load_dotenv
from microsoft_agents.copilotstudio.client import (
    CopilotClient,
    PowerPlatformCloud,
    AgentType,
    ConnectionSettings,
)
from microsoft_agents.activity import ActivityTypes
from azure.identity import InteractiveBrowserCredential, DefaultAzureCredential


class AutomatedCopilotStudioAgent:
    def __init__(self):
        try:
            load_dotenv()

            # Load configuration from .env
            self.app_client_id = os.getenv("COPILOT_STUDIO_AGENT_APP_CLIENT_ID")
            self.tenant_id = os.getenv("COPILOT_STUDIO_AGENT_TENANT_ID")
            self.environment_id = os.getenv("COPILOT_STUDIO_AGENT_ENVIRONMENT_ID")
            self.agent_id = os.getenv("COPILOT_STUDIO_AGENT_AGENT_IDENTIFIER")
            self.auth_mode = os.getenv("COPILOT_STUDIO_AGENT_AUTH_MODE", "interactive")

            self.client = None
            self.conversation_id = None
            self.is_initialized = False

            # Validate configuration
            missing_vars = []
            if not self.app_client_id:
                missing_vars.append("COPILOT_STUDIO_AGENT_APP_CLIENT_ID")
            if not self.tenant_id:
                missing_vars.append("COPILOT_STUDIO_AGENT_TENANT_ID")
            if not self.environment_id:
                missing_vars.append("COPILOT_STUDIO_AGENT_ENVIRONMENT_ID")
            if not self.agent_id:
                missing_vars.append("COPILOT_STUDIO_AGENT_AGENT_IDENTIFIER")

            if missing_vars:
                raise ValueError(
                    f"Missing required environment variables: {', '.join(missing_vars)}. Check your .env file."
                )

        except Exception:
            raise

    async def initialize(self):
        """Initialize the Copilot Studio client with authentication"""
        if self.is_initialized:
            return True

        try:
            # Set up authentication based on mode
            if self.auth_mode == "interactive":
                credential = InteractiveBrowserCredential(
                    client_id=self.app_client_id, tenant_id=self.tenant_id
                )
            else:
                credential = DefaultAzureCredential()

            # Get access token using the specific scope that your app has permissions for
            access_token = None
            scopes_to_try = [
                "8578e004-a5c6-46e7-913e-12f58912df43/.default",
                "00000003-0000-0000-c000-000000000000/.default",
            ]

            for scope in scopes_to_try:
                try:
                    token_result = await asyncio.wait_for(
                        asyncio.to_thread(credential.get_token, scope), timeout=30.0
                    )
                    access_token = token_result.token
                    break
                except (asyncio.TimeoutError, Exception):
                    continue

            if not access_token:
                raise Exception("Failed to get token with any available scopes")

            # Create connection settings
            settings = ConnectionSettings(
                environment_id=self.environment_id,
                agent_identifier=self.agent_id,
                cloud=PowerPlatformCloud.PROD,
                copilot_agent_type=AgentType.PUBLISHED,
                custom_power_platform_cloud=None,
            )

            # Initialize client
            self.client = CopilotClient(settings=settings, token=access_token)
            self.is_initialized = True
            print("✅ Connected to Copilot Studio agent")
            return True

        except Exception as e:
            print(f"❌ Error initializing Copilot Studio client: {e}")
            self.client = None
            self.is_initialized = False
            return False

    async def send_message(self, message: str) -> str:
        """Send a message to the Copilot Studio agent and get response"""
        if not message or not message.strip():
            return "Error: Empty message"

        try:
            # Ensure client is initialized
            if not self.client or not self.is_initialized:
                if not await self.initialize():
                    return "Error: Failed to initialize client"

            # Start conversation if needed
            if not self.conversation_id:
                try:
                    async with asyncio.timeout(30.0):
                        async for activity in self.client.start_conversation():
                            if (
                                activity
                                and hasattr(activity, "conversation")
                                and activity.conversation
                            ):
                                if (
                                    hasattr(activity.conversation, "id")
                                    and activity.conversation.id
                                ):
                                    self.conversation_id = activity.conversation.id
                                    break

                    if not self.conversation_id:
                        return "Error: Failed to start conversation"

                except asyncio.TimeoutError:
                    return "Error: Timeout starting conversation"
                except Exception as e:
                    return f"Error starting conversation: {e}"

            # Get response from agent with timeout
            try:
                responses = []

                async with asyncio.timeout(60.0):
                    async for activity in self.client.ask_question(
                        message, self.conversation_id
                    ):
                        if not activity:
                            continue

                        if (
                            hasattr(activity, "type")
                            and activity.type == ActivityTypes.message
                        ):
                            # Check for direct text
                            if hasattr(activity, "text") and activity.text:
                                responses.append(str(activity.text))

                            # Check attachments for Adaptive Cards
                            elif (
                                hasattr(activity, "attachments")
                                and activity.attachments
                            ):
                                for attachment in activity.attachments:
                                    if not attachment or not hasattr(
                                        attachment, "content"
                                    ):
                                        continue

                                    if attachment.content and isinstance(
                                        attachment.content, dict
                                    ):
                                        if "body" in attachment.content and isinstance(
                                            attachment.content["body"], list
                                        ):
                                            card_texts = []
                                            for item in attachment.content["body"]:
                                                if (
                                                    isinstance(item, dict)
                                                    and item.get("type") == "TextBlock"
                                                    and "text" in item
                                                ):
                                                    card_texts.append(str(item["text"]))
                                            if card_texts:
                                                responses.append(" ".join(card_texts))

                return " ".join(responses) if responses else "No response received"

            except asyncio.TimeoutError:
                return "Error: Timeout waiting for response"
            except Exception as e:
                return f"Error getting response: {e}"

        except Exception as e:
            return f"Error: {e}"

    async def _show_thinking(self):
        """Show animated thinking dots"""
        dots = ""
        try:
            while True:
                for i in range(4):
                    dots = "." * i
                    print(f"\r🤖 Agent: Thinking{dots}   ", end="", flush=True)
                    await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            pass

    async def interactive_session(self):
        """Run an interactive chat session"""
        print("🤖 Copilot Studio Fashion Database Assistant")
        print("Ask me anything about the fashion database!")
        print("Type 'quit', 'exit', or 'q' to end the session")
        print("=" * 50)

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

                # Rate limiting - simple delay between requests
                if retry_count > 0:
                    await asyncio.sleep(min(2**retry_count, 10))

                print("🤖 Agent: Thinking", end="", flush=True)

                # Show thinking dots
                thinking_task = asyncio.create_task(self._show_thinking())

                try:
                    response = await asyncio.wait_for(
                        self.send_message(user_input), timeout=120.0
                    )
                    thinking_task.cancel()
                    print(f"\r🤖 Agent: {response}")
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


async def main():
    """Interactive Copilot Studio Agent"""
    agent = None
    try:
        agent = AutomatedCopilotStudioAgent()

        if not await agent.initialize():
            print("❌ Failed to initialize agent")
            return

        await agent.interactive_session()

    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        if agent:
            agent.client = None
            agent.conversation_id = None
            agent.is_initialized = False


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Application terminated")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
