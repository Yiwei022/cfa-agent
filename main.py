#!/usr/bin/env python3
"""Main CLI entry point for the agentic chatbot."""
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.theme import Theme
from rich.text import Text
from agent import Agent
from memory import load_memory, save_memory, get_memory_size_kb
from config import MEMORY_THRESHOLD_KB

# ASCII Art - Complete block
ASCII_AIVANCITY = """
            ███                                             ███   █████              
           ░░░                                             ░░░   ░░███               
  ██████   ████  █████ █████  ██████   ████████    ██████  ████  ███████   █████ ████
 ░░░░░███ ░░███ ░░███ ░░███  ░░░░░███ ░░███░░███  ███░░███░░███ ░░░███░   ░░███ ░███ 
  ███████  ░███  ░███  ░███   ███████  ░███ ░███ ░███ ░░░  ░███   ░███     ░███ ░███ 
 ███░░███  ░███  ░░███ ███   ███░░███  ░███ ░███ ░███  ███ ░███   ░███ ███ ░███ ░███ 
░░████████ █████  ░░█████   ░░████████ ████ █████░░██████  █████  ░░█████  ░░███████ 
 ░░░░░░░░ ░░░░░    ░░░░░     ░░░░░░░░ ░░░░ ░░░░░  ░░░░░░  ░░░░░    ░░░░░    ░░░░░███ 
                                                                            ███ ░███ 
                                                                           ░░██████  
                                                                            ░░░░░░   """

# Position where "ai" ends and "vancity" begins (character index per line)
COLOR_CHANGE_POSITION = 16  # Adjust this if needed after testing

ASCII_AGENT = """
                                         █████   
                                        ░░███    
  ██████    ███████  ██████  ████████   ███████  
 ░░░░░███  ███░░███ ███░░███░░███░░███ ░░░███░   
  ███████ ░███ ░███░███████  ░███ ░███   ░███    
 ███░░███ ░███ ░███░███░░░   ░███ ░███   ░███ ███
░░████████░░███████░░██████  ████ █████  ░░█████ 
 ░░░░░░░░  ░░░░░███ ░░░░░░  ░░░░ ░░░░░    ░░░░░  
           ███ ░███                              
          ░░██████                               
           ░░░░░░                                """

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
    # Split the aivancity ASCII art into lines
    aivancity_lines = ASCII_AIVANCITY.strip("\n").split("\n")

    # Create Text object for the banner
    banner = Text()

    # Process each line: color "ai" part brown, "vancity" part blue
    for i, line in enumerate(aivancity_lines):
        if len(line) > COLOR_CHANGE_POSITION:
            # Split at the color change position
            ai_part = line[:COLOR_CHANGE_POSITION]
            vancity_part = line[COLOR_CHANGE_POSITION:]

            # Add colored parts
            banner.append(ai_part, style="user")  # "ai" in brown
            banner.append(vancity_part, style="assistant")  # "vancity" in blue
        else:
            # Line is shorter than change position, color it all as "ai"
            banner.append(line, style="user")

        # Add newline except for last line
        if i < len(aivancity_lines) - 1:
            banner.append("\n")

    # Add spacing between "aivancity" and "agent"
    banner.append("\n\n")

    # Add "agent" below in grey
    banner.append(ASCII_AGENT.strip("\n"), style="dim")

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
    percentage = (size_kb / MEMORY_THRESHOLD_KB) * 100

    stats_text =Markdown(f"""
- **Message Count:** {len(messages)} messages
- **Memory Size:** {size_kb:.2f} KB / {MEMORY_THRESHOLD_KB} KB ({percentage:.1f}%)
- **Status:** {'[warning]⚠️  Approaching threshold[/warning]' if size_kb > MEMORY_THRESHOLD_KB * 0.8 else '[success]✓ Healthy[/success]'}
    """)
    console.print(Panel(stats_text, title="[bold user]Memory Statistics[/bold user]", border_style="user"))


def main():
    """Main CLI chat loop."""
    # Print ASCII art banner
    console.print()
    print_ascii_banner()
    console.print()
    console.print("[dim]Powered by OpenAI with Function Calling[/dim]", justify="center")
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

    # Main chat loop
    while True:
        try:
            # Get user input with Rich prompt
            user_input = Prompt.ask("[bold user]You[/bold user]").strip()

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
