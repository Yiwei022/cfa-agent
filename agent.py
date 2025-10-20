"""Mistral AI agent with function calling support."""
import json
import time
from typing import List, Dict, Any
from mistralai import Mistral
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.live import Live
from rich.spinner import Spinner
from config import MISTRAL_API_KEY, MISTRAL_MODEL, MAX_TOOL_ROUNDS, MISTRAL_MIN_DELAY, load_prompts
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
        self.last_api_call_time = 0  # Track last API call for rate limiting

    def _rate_limit(self):
        """Enforce rate limiting by sleeping if necessary.

        Ensures minimum delay between API calls to respect Mistral's rate limits.
        Free tier: 1 request per second (RPS).
        """
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call_time

        if time_since_last_call < MISTRAL_MIN_DELAY:
            sleep_time = MISTRAL_MIN_DELAY - time_since_last_call
            time.sleep(sleep_time)

        self.last_api_call_time = time.time()

    def process_message(self, messages: List[Dict[str, Any]], user_input: str) -> tuple[List[Dict[str, Any]], str]:
        """Process user input and generate response with tool calling.

        Args:
            messages: Conversation history
            user_input: User's input message

        Returns:
            Tuple of (updated_messages, assistant_response)
        """
        # Store original length to rollback on error
        original_length = len(messages)

        try:
            # Add user message
            messages.append({"role": "user", "content": user_input})

            # Check if we need to summarize memory
            if should_summarize(messages):
                self.console.print("[warning]⚠️  Memory threshold reached, summarizing conversation...[/warning]")
                messages = self._summarize_and_compress(messages)
                # Update original_length after summarization
                original_length = len(messages) - 1  # -1 because we just added user message

            # Tool calling loop - allow multiple rounds of tool execution
            tool_round = 0
            while tool_round < MAX_TOOL_ROUNDS:
                # Prepare messages with system prompt
                api_messages = [{"role": "system", "content": self.system_prompt}] + messages

                # Apply rate limiting before API call
                self._rate_limit()

                # Call Mistral API with tools (with spinner)
                spinner_text = "[dim]Thinking...[/dim]" if tool_round == 0 else "[dim]Processing tool results...[/dim]"
                with Live(Spinner("dots", text=spinner_text), console=self.console, transient=True):
                    response = self.client.chat.complete(
                        model=self.model,
                        messages=api_messages,
                        tools=TOOL_SCHEMAS,
                    )

                assistant_message = response.choices[0].message

                # Check if agent wants to call tools
                if assistant_message.tool_calls:
                    tool_round += 1

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

                    # Execute tools and add results to messages
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

                    # Continue loop to let agent process tool results
                    continue

                else:
                    # No tool calls - agent is done, return final response
                    content = assistant_message.content or ""
                    if content.strip():  # Only add if there's actual content
                        messages.append({"role": "assistant", "content": content})
                    return messages, content

            # If we hit MAX_TOOL_ROUNDS, return a warning message
            warning = f"Maximum tool rounds ({MAX_TOOL_ROUNDS}) reached. Stopping tool execution."
            self.console.print(f"[warning]⚠️  {warning}[/warning]")
            messages.append({"role": "assistant", "content": warning})
            return messages, warning

        except Exception as e:
            # Rollback messages to original state on error
            del messages[original_length:]

            # Add detailed error information for debugging
            error_msg = str(e)
            if hasattr(e, 'response'):
                error_msg = f"{error_msg}\nResponse: {e.response}"
            if hasattr(e, 'status_code'):
                error_msg = f"API error occurred: Status {e.status_code}\n{e.response.text if hasattr(e, 'response') else str(e)}"

            # Re-raise with enhanced error message
            raise Exception(error_msg) from e

    def _summarize_and_compress(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Summarize conversation and compress memory.

        Args:
            messages: Current conversation history

        Returns:
            Compressed message history
        """
        # Create summarization request
        summary_prompt = create_summary_request(messages, self.prompts["summarization_prompt"])

        # Apply rate limiting before API call
        self._rate_limit()

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
