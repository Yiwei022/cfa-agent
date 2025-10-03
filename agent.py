"""Mistral AI agent with function calling support."""
import json
from typing import List, Dict, Any
from mistralai import Mistral
from config import MISTRAL_API_KEY, MISTRAL_MODEL, load_prompts
from tools import TOOL_SCHEMAS, execute_tool
from memory import should_summarize, create_summary_request, compress_memory


class Agent:
    """AI agent powered by Mistral with tool calling capabilities."""

    def __init__(self):
        """Initialize the agent with Mistral client and prompts."""
        if not MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY environment variable not set")

        self.client = Mistral(api_key=MISTRAL_API_KEY)
        self.model = MISTRAL_MODEL
        self.prompts = load_prompts()
        self.system_prompt = self.prompts["system_prompt"]

    def process_message(self, messages: List[Dict[str, Any]], user_input: str) -> tuple[List[Dict[str, Any]], str]:
        """Process user input and generate response with tool calling.

        Args:
            messages: Conversation history
            user_input: User's input message

        Returns:
            Tuple of (updated_messages, assistant_response)
        """
        # Add user message
        messages.append({"role": "user", "content": user_input})

        # Check if we need to summarize memory
        if should_summarize(messages):
            print("[Memory threshold reached, summarizing conversation...]")
            messages = self._summarize_and_compress(messages)

        # Prepare messages with system prompt
        api_messages = [{"role": "system", "content": self.system_prompt}] + messages

        # Call Mistral API with tools
        response = self.client.chat.complete(
            model=self.model,
            messages=api_messages,
            tools=TOOL_SCHEMAS,
        )

        assistant_message = response.choices[0].message

        # Handle tool calls if present
        if assistant_message.tool_calls:
            # Add assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })

            # Execute tools and collect results
            tool_results = []
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                print(f"[Executing tool: {tool_name} with args: {tool_args}]")

                result = execute_tool(tool_name, tool_args)
                tool_results.append(result)

                # Add tool result message
                messages.append({
                    "role": "tool",
                    "name": tool_name,
                    "tool_call_id": tool_call.id,
                    "content": result
                })

            # Call API again with tool results
            api_messages = [{"role": "system", "content": self.system_prompt}] + messages
            final_response = self.client.chat.complete(
                model=self.model,
                messages=api_messages,
                tools=TOOL_SCHEMAS,
            )

            final_message = final_response.choices[0].message
            messages.append({"role": "assistant", "content": final_message.content})

            return messages, final_message.content

        else:
            # No tool calls, just return the response
            messages.append({"role": "assistant", "content": assistant_message.content})
            return messages, assistant_message.content

    def _summarize_and_compress(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Summarize conversation and compress memory.

        Args:
            messages: Current conversation history

        Returns:
            Compressed message history
        """
        # Create summarization request
        summary_prompt = create_summary_request(messages, self.prompts["summarization_prompt"])

        # Call Mistral to generate summary
        summary_response = self.client.chat.complete(
            model=self.model,
            messages=[{"role": "user", "content": summary_prompt}]
        )

        summary = summary_response.choices[0].message.content

        # Compress memory with summary
        return compress_memory(messages, summary)
