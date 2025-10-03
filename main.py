#!/usr/bin/env python3
"""Main CLI entry point for the agentic chatbot."""
import sys
from agent import Agent
from memory import load_memory, save_memory


def print_help():
    """Print help message."""
    print("""
Available commands:
  /help    - Show this help message
  /clear   - Clear conversation history
  /exit    - Exit the chatbot
  /quit    - Exit the chatbot

Just type your message to chat with the agent!
    """)


def main():
    """Main CLI chat loop."""
    print("=" * 60)
    print("  Simple Agentic CLI Chatbot")
    print("  Powered by Mistral AI")
    print("=" * 60)
    print("\nType /help for commands, /exit to quit\n")

    # Initialize agent
    try:
        agent = Agent()
    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease set MISTRAL_API_KEY environment variable:")
        print("  export MISTRAL_API_KEY='your-api-key'")
        sys.exit(1)
    except Exception as e:
        print(f"Error initializing agent: {e}")
        sys.exit(1)

    # Load conversation history
    messages = load_memory()
    if messages:
        print(f"[Loaded {len(messages)} messages from previous session]\n")

    # Main chat loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith("/"):
                command = user_input.lower()

                if command in ["/exit", "/quit"]:
                    print("\nSaving conversation and exiting...")
                    save_memory(messages)
                    print("Goodbye!")
                    break

                elif command == "/help":
                    print_help()
                    continue

                elif command == "/clear":
                    messages = []
                    save_memory(messages)
                    print("[Conversation history cleared]\n")
                    continue

                else:
                    print(f"Unknown command: {user_input}")
                    print("Type /help for available commands\n")
                    continue

            # Process message with agent
            try:
                messages, response = agent.process_message(messages, user_input)
                print(f"\nAssistant: {response}\n")

                # Save after each interaction
                save_memory(messages)

            except Exception as e:
                print(f"\nError processing message: {e}\n")
                # Continue the loop even if there's an error

        except KeyboardInterrupt:
            print("\n\nInterrupted. Saving conversation...")
            save_memory(messages)
            print("Goodbye!")
            break

        except EOFError:
            print("\n\nSaving conversation...")
            save_memory(messages)
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
