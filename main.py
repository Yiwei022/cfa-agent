#!/usr/bin/env python3
"""Main CLI entry point for the FLE agent."""
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.theme import Theme
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style as PTStyle
from agent import Agent
from memory import load_memory, save_memory, get_memory_size_kb

# ASCII Art - Complete block
ASCII_FLE_AGENT = """
 ███████ ██      ███████      █████   ██████  ███████ ███    ██ ████████ 
 ██      ██      ██          ██   ██ ██       ██      ████   ██    ██    
 █████   ██      █████       ███████ ██   ███ █████   ██ ██  ██    ██    
 ██      ██      ██          ██   ██ ██    ██ ██      ██  ██ ██    ██    
 ██      ███████ ███████     ██   ██  ██████  ███████ ██   ████    ██    """

# Position where "FLE" ends and "agent" begins (character index per line)
FLE_END_POSITION = 25  # Where FLE ends
AGENT_START_POSITION = 29  # Where "agent" starts

# Initialize Rich console with custom theme
console = Console(theme=Theme({
    "user": "#6FD3D3 bold",      # Custom brown for user (ai)
    "assistant": "#D36FB6",      # Custom blue for assistant (vancity)
    "tool": "yellow",
    "success": "green",
    "warning": "yellow",
    "error": "red bold",
    "dim": "dim"
}))


def print_ascii_banner():
    """Print the ASCII art banner with colored sections."""
    # Split the FLE agent ASCII art into lines
    fle_agent_lines = ASCII_FLE_AGENT.strip("\n").split("\n")

    # Create Text object for the banner
    banner = Text()

    # Process each line: color "F" in user color, "LE" in assistant color, "agent" in white
    for i, line in enumerate(fle_agent_lines):
        if len(line) > AGENT_START_POSITION:
            # Split into three parts: F, LE, and agent
            f_part = line[:9]  # "F" part
            le_part = line[9:FLE_END_POSITION]  # "LE" part
            space_part = line[FLE_END_POSITION:AGENT_START_POSITION]  # spacing
            agent_part = line[AGENT_START_POSITION:]  # "agent" part

            # Add colored parts
            banner.append(f_part, style="user")  # "F" in cyan
            banner.append(le_part, style="assistant")  # "LE" in magenta
            banner.append(space_part)  # spacing (default color)
            banner.append(agent_part, style="white")  # "agent" in white
        else:
            # Fallback for shorter lines
            banner.append(line, style="user")

        # Add newline except for last line
        if i < len(fle_agent_lines) - 1:
            banner.append("\n")

    # Print in a panel
    console.print(Panel(
        banner,
        border_style="user",
        padding=(1, 2)
    ))


def print_help():
    """Print help message."""
    help_text = """
**Available commands:**

• `/help` - Show this help message
• `/clear` - Clear conversation history
• `/reset` - Reset conversation (alias for /clear)
• `/stats` - Show memory statistics
• `/exit` or `/quit` - Exit the chatbot

Just type your message to chat with the agent!
    """
    console.print(Panel(help_text.strip(), title="[bold user]Help[/bold user]", border_style="user"))


def print_stats(messages):
    """Print memory statistics."""
    size_kb = get_memory_size_kb(messages)

    stats_text = Markdown(f"""
- **Message Count:** {len(messages)} messages (local display history)
- **Local Storage Size:** {size_kb:.2f} KB
- **API State:** Managed server-side by Responses API
- **Note:** Conversation state is tracked automatically via response IDs
    """)
    console.print(Panel(stats_text, title="[bold user]Memory Statistics[/bold user]", border_style="user"))


def main():
    """Main CLI chat loop."""
    # Print ASCII art banner
    console.print()
    print_ascii_banner()
    console.print()
    console.print("[dim]Powered by OpenAI Responses API with Stateful Conversations[/dim]", justify="center")
    console.print("[dim]Type /help for commands, /exit to quit[/dim]\n", justify="center")

    # Initialize agent
    try:
        agent = Agent(console)
    except ValueError as e:
        console.print(f"[error]Error:[/error] {e}")
        console.print("\n[warning]Please set OPENAI_API_KEY environment variable:[/warning]")
        console.print("  [dim]export OPENAI_API_KEY='your-api-key'[/dim]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[error]Error initializing agent:[/error] {e}")
        sys.exit(1)

    # Load conversation history
    messages = load_memory()
    if messages:
        console.print(f"[dim]✓ Loaded {len(messages)} messages from previous session[/dim]\n")

    # Check for new week on startup
    from tools import check_new_week_status
    week_status = check_new_week_status()
    
    # Only show if it's a new week or if there's a goal set
    if "NEW WEEK" in week_status or "Current Week" in week_status:
        console.print(Panel(
            Markdown(week_status),
            title="[bold user]📅 Week Status[/bold user]",
            border_style="user"
        ))
        console.print()

    # Initialize prompt_toolkit session with basic arrow key navigation and mouse support
    # Supports: 
    # - Arrow keys (left/right navigation, up/down history)
    # - Mouse (click to position cursor, click and drag to select text)
    # - Backspace/Delete (including deletion of selected text)
    prompt_style = PTStyle.from_dict({
        'prompt': '#6FD3D3 bold',  # Match the user color theme
    })
    
    session = PromptSession(
        history=InMemoryHistory(),
        style=prompt_style,
        enable_history_search=False,  # Keep it simple - no Ctrl+R reverse search
        vi_mode=False,
    )

    # Main chat loop
    while True:
        try:
            # Get user input with prompt_toolkit (supports arrow keys, history, and mouse)
            user_input = session.prompt(
                [('class:prompt', 'You: ')],
                mouse_support=True  # Enable mouse: click to position, drag to select text
            ).strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith("/"):
                command = user_input.lower()

                if command in ["/exit", "/quit"]:
                    console.print("\n[dim]Saving conversation and exiting...[/dim]")
                    save_memory(messages)
                    console.print("[success]Goodbye! 👋[/success]")
                    break

                elif command == "/help":
                    print_help()
                    continue

                elif command in ["/clear", "/reset"]:
                    messages = []
                    agent.reset_conversation()  # Reset Responses API conversation state
                    save_memory(messages)
                    console.print("[success]✓ Conversation history cleared[/success]\n")
                    continue

                elif command == "/stats":
                    print_stats(messages)
                    continue

                else:
                    console.print(f"[warning]Unknown command:[/warning] {user_input}")
                    console.print("[dim]Type /help for available commands[/dim]\n")
                    continue

            # Display user message in a panel
            console.print(Panel(user_input, title="[bold user]👤 You[/bold user]", border_style="user"))

            # Process message with agent
            try:
                messages, response = agent.process_message(messages, user_input)

                # Display assistant response with markdown rendering
                md = Markdown(response)
                console.print(Panel(md, title="[bold assistant]🤖 Assistant[/bold assistant]", border_style="assistant"))
                console.print()  # Add spacing

                # Save after each interaction
                save_memory(messages)

            except Exception as e:
                console.print(Panel(
                    f"[error]Error:[/error] {str(e)}",
                    title="[bold red]❌ Error[/bold red]",
                    border_style="red"
                ))
                console.print()
                # Continue the loop even if there's an error

        except KeyboardInterrupt:
            console.print("\n\n[dim]Interrupted. Saving conversation...[/dim]")
            save_memory(messages)
            console.print("[success]Goodbye! 👋[/success]")
            break

        except EOFError:
            console.print("\n\n[dim]Saving conversation...[/dim]")
            save_memory(messages)
            console.print("[success]Goodbye! 👋[/success]")
            break


if __name__ == "__main__":
    main()
