"""Mistral AI agent with function calling support."""
import json
from typing import List, Dict, Any
from mistralai import Mistral
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.live import Live
from rich.spinner import Spinner
from config import MISTRAL_API_KEY, MISTRAL_MODEL, load_prompts
from tools import TOOL_SCHEMAS, execute_tool
from memory import should_summarize, create_summary_request, compress_memory


class Agent:
    """AI agent powered by Mistral with tool calling capabilities."""

    def __init__(self, console: Console = None):
        """Initialize the agent with Mistral client and prompts.

        Args:
            console: Rich Console instance for formatted output (optional)
        """
        if not MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY environment variable not set")

        self.client = Mistral(api_key=MISTRAL_API_KEY)
        self.model = MISTRAL_MODEL
        self.prompts = load_prompts()
        self.system_prompt = self.prompts["system_prompt"]
        self.console = console or Console()

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
            self.console.print("[warning]⚠️  Memory threshold reached, summarizing conversation...[/warning]")
            messages = self._summarize_and_compress(messages)

        # Prepare messages with system prompt
        api_messages = [{"role": "system", "content": self.system_prompt}] + messages

        # Call Mistral API with tools (with spinner)
        with Live(Spinner("dots", text="[dim]Thinking...[/dim]"), console=self.console, transient=True):
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

                # Display tool execution with rich formatting
                args_json = json.dumps(tool_args, indent=2)
                syntax = Syntax(args_json, "json", theme="monokai", line_numbers=False)

                tool_panel = Panel(
                    syntax,
                    title=f"[bold tool]⚙️  Executing: {tool_name}[/bold tool]",
                    border_style="tool"
                )
                self.console.print(tool_panel)

                result = execute_tool(tool_name, tool_args)
                tool_results.append(result)

                # Display tool result
                result_panel = Panel(
                    f"[dim]{result}[/dim]",
                    title=f"[bold tool]✓ Result[/bold tool]",
                    border_style="tool"
                )
                self.console.print(result_panel)

                # Add tool result message
                messages.append({
                    "role": "tool",
                    "name": tool_name,
                    "tool_call_id": tool_call.id,
                    "content": result
                })

            # Call API again with tool results (with spinner)
            api_messages = [{"role": "system", "content": self.system_prompt}] + messages
            with Live(Spinner("dots", text="[dim]Generating response...[/dim]"), console=self.console, transient=True):
                final_response = self.client.chat.complete(
                    model=self.model,
                    messages=api_messages,
                    tools=TOOL_SCHEMAS,
                )

            final_message = final_response.choices[0].message
            final_content = final_message.content or ""

            # Handle edge case: empty response after tool execution
            if not final_content and not final_message.tool_calls:
                # Mistral sometimes returns empty response after tool errors
                final_content = "I apologize, I encountered an issue processing that request. Please try again."
            
            messages.append({"role": "assistant", "content": final_content})

            return messages, final_content

        else:
            # No tool calls, just return the response
            content = assistant_message.content or ""
            messages.append({"role": "assistant", "content": content})
            return messages, content

    def _summarize_and_compress(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Summarize conversation and compress memory.

        Args:
            messages: Current conversation history

        Returns:
            Compressed message history
        """
        # Create summarization request
        summary_prompt = create_summary_request(messages, self.prompts["summarization_prompt"])

        # Call Mistral to generate summary (with spinner)
        with Live(Spinner("dots", text="[dim]Summarizing conversation...[/dim]"), console=self.console, transient=True):
            summary_response = self.client.chat.complete(
                model=self.model,
                messages=[{"role": "user", "content": summary_prompt}]
            )

        summary = summary_response.choices[0].message.content

        # Compress memory with summary
        compressed = compress_memory(messages, summary)
        self.console.print(f"[success]✓ Memory compressed: {len(messages)} → {len(compressed)} messages[/success]")

        return compressed
