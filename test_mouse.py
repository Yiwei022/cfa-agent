#!/usr/bin/env python3
"""Test script to verify mouse support in prompt_toolkit."""
from prompt_toolkit import PromptSession

print("Testing mouse support in prompt_toolkit...")
print("Try the following:")
print("  1. Click anywhere in the input line to position cursor")
print("  2. Click and drag to select text")
print("  3. Press backspace to delete selected text")
print("  4. Type 'exit' and press Enter to quit\n")

session = PromptSession()

while True:
    try:
        user_input = session.prompt(
            'Test> ',
            mouse_support=True
        ).strip()
        
        if user_input.lower() == 'exit':
            print("Exiting test...")
            break
        
        print(f"You entered: {user_input}")
        
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting...")
        break
    except EOFError:
        print("\nEOF. Exiting...")
        break

