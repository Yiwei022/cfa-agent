"""Agent using OpenAI Responses API"""
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.live import Live
from rich.spinner import Spinner
from config import OPENAI_API_KEY, OPENAI_MODEL, load_prompts
from tools import TOOL_SCHEMAS, execute_tool


class Agent:
    """AI agent powered by OpenAI Responses API with stateful conversations."""

    def __init__(self, console: Console = None):
        """Initialize the agent with OpenAI client and prompts.

        Args:
            console: Rich Console instance for formatted output (optional)
        """
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.prompts = load_prompts()
        self.system_prompt = self.prompts["system_prompt"]
        self.console = console or Console()
        self.last_response_id: Optional[str] = None  # Track conversation state

    def reset_conversation(self):
        """Reset the conversation state (for /clear command)."""
        self.last_response_id = None

    def process_message(self, messages: List[Dict[str, Any]], user_input: str) -> tuple[List[Dict[str, Any]], str]:
        """Process user input and generate response using Responses API.

        Args:
            messages: Conversation history (kept for backwards compatibility and display)
            user_input: User's input message

        Returns:
            Tuple of (updated_messages, assistant_response)
        """
        # Add user message to local history (for display/logging purposes)
        messages.append({"role": "user", "content": user_input})

        # Call Responses API with stateful conversation tracking
        with Live(Spinner("dots", text="[dim]Thinking...[/dim]"), console=self.console, transient=True):
            try:
                response = self.client.responses.create(
                    model=self.model,
                    instructions=self.system_prompt,  # System prompt as instructions
                    input=user_input,  # Current user message
                    previous_response_id=self.last_response_id,  # Maintain conversation state
                    tools=TOOL_SCHEMAS,
                    reasoning_effort="minimal",
                )
            except Exception as e:
                # Fallback error handling
                error_msg = f"API Error: {str(e)}"
                self.console.print(f"[error]{error_msg}[/error]")
                messages.append({"role": "assistant", "content": error_msg})
                return messages, error_msg

        # Store response ID for next call
        self.last_response_id = response.id

        # Extract the main response content
        assistant_content = ""
        tool_calls_made = []
        
        # Handle different output types from Responses API
        if hasattr(response, 'output') and response.output:
            for output in response.output:
                output_type = getattr(output, 'type', None)
                
                if output_type == "message":
                    # Text response
                    if hasattr(output, 'content'):
                        for content_part in output.content:
                            if hasattr(content_part, 'text'):
                                assistant_content += content_part.text
                            elif isinstance(content_part, str):
                                assistant_content += content_part
                
                elif output_type == "function_call":
                    # Tool call detected - execute it
                    tool_name = output.function.name
                    tool_args = json.loads(output.function.arguments) if isinstance(output.function.arguments, str) else output.function.arguments

                    # Display tool execution
                    args_json = json.dumps(tool_args, indent=2)
                    syntax = Syntax(args_json, "json", theme="monokai", line_numbers=False)
                    tool_panel = Panel(
                        syntax,
                        title=f"[bold tool]⚙️  Executing: {tool_name}[/bold tool]",
                        border_style="tool"
                    )
                    self.console.print(tool_panel)

                    # Execute tool
                    result = execute_tool(tool_name, tool_args)
                    tool_calls_made.append({"name": tool_name, "result": result})

                    # Display result
                    result_panel = Panel(
                        f"[dim]{result}[/dim]",
                        title=f"[bold tool]✓ Result[/bold tool]",
                        border_style="tool"
                    )
                    self.console.print(result_panel)

                    # Add tool execution to local history
                    messages.append({
                        "role": "tool",
                        "name": tool_name,
                        "content": result
                    })

        # Fallback: try alternative response structure
        if not assistant_content and not tool_calls_made:
            # Try to extract from different response structure
            if hasattr(response, 'content'):
                if isinstance(response.content, list):
                    for item in response.content:
                        if hasattr(item, 'text'):
                            assistant_content += item.text
                elif isinstance(response.content, str):
                    assistant_content = response.content
            elif hasattr(response, 'message'):
                assistant_content = response.message.get('content', '')

        # Add assistant response to local history
        if assistant_content:
            messages.append({"role": "assistant", "content": assistant_content})
        elif tool_calls_made:
            # If we only had tool calls, the API might send another response with the final message
            # For now, add a placeholder
            assistant_content = "[Tool execution completed]"
            messages.append({"role": "assistant", "content": assistant_content})
        else:
            # No content at all
            assistant_content = "I apologize, I encountered an issue generating a response."
            messages.append({"role": "assistant", "content": assistant_content})

        return messages, assistant_content
