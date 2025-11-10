# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a pedagogical demonstration of AI agents with function calling using the Mistral API. It's a simple agentic CLI chatbot built for the PGE3-EN Coding for AI course at Aivancity (2025-2026). The codebase is intentionally minimal to demonstrate core agentic concepts clearly.

## Development Commands

### Setup
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# OR .venv\Scripts\activate  # Windows
pip install -r requirements.txt
echo "MISTRAL_API_KEY=your-key" > .env
```

### Running
```bash
python main.py  # Start the chatbot
```

### Testing
```bash
python -m pytest tests/ -v              # Run all tests (18 tests total)
python -m pytest tests/test_core.py -v  # Test tools and config only
python -m pytest tests/test_memory.py -v # Test memory management only
python -m pytest <path>::<test_name> -v # Run single test
```

## Architecture

### Core Agent Loop
The agent follows a multi-step API call pattern for function calling:

1. User sends message → Added to conversation history
2. Check if memory threshold exceeded → Summarize if needed
3. **First API call**: Agent receives message + tool schemas, decides whether to call tools
4. If tools called: Execute Python functions, add results to conversation
5. **Second API call**: Agent receives tool results, generates final response

This two-call pattern is fundamental to how function calling works with Mistral API.

### File Responsibilities

- **[main.py](main.py)** - CLI chat loop, command handling (`/exit`, `/clear`, `/help`, `/reset`), saves memory on exit/interrupt
- **[agent.py](agent.py)** - Mistral API integration, implements the two-call tool execution pattern, handles memory compression
- **[tools.py](tools.py)** - Tool implementations (Python functions), tool schemas (JSON), tool registry (dict mapping names to functions), execution dispatcher
- **[memory.py](memory.py)** - JSON persistence, size calculation (KB-based), summarization logic (keep last N + summary)
- **[config.py](config.py)** - Environment variables, model selection (`mistral-small-latest`), thresholds (`MEMORY_THRESHOLD_KB=50`, `MEMORY_KEEP_LAST_N=10`)
- **[prompts.yaml](prompts.yaml)** - System prompt (agent behavior), summarization prompt (memory compression)

### Memory Management Strategy

When conversation exceeds `MEMORY_THRESHOLD_KB` (50KB):
1. Agent calls Mistral API with summarization prompt
2. Old messages (beyond last 10) → Compressed into summary
3. Recent messages (last 10) → Kept verbatim
4. New format: `[summary_message] + recent_messages`
5. This "sliding window" keeps context manageable

Why this matters: LLMs have token limits. This simple KB-based heuristic prevents exceeding them while preserving recent context.

### Tool System Architecture

**Three components must stay synchronized:**

1. **Function implementation** - Actual Python function with docstring
2. **TOOL_FUNCTIONS registry** - `{"tool_name": function_reference}`
3. **TOOL_SCHEMAS** - JSON schema describing function for the LLM

When adding a tool, update all three in [tools.py](tools.py).

**Tool execution contract:**
- Tools always return strings (agent sees these)
- Handle errors gracefully (return error messages, don't raise)
- Provide clear success/failure messages for LLM to understand

## Key Design Principles

1. **Simplicity over features** - Intentionally minimal to demonstrate concepts
2. **Clear data flow** - Message format follows standard chat API conventions
3. **Pedagogical focus** - Code structure mirrors the README explanations
4. **No overengineering** - Direct implementations, no abstractions that obscure learning

## Important Conventions

### Message Format
Standard chat API format:
```python
{"role": "user|assistant|system|tool", "content": str, "tool_calls": [...]}  # optional tool_calls
```

### Tool Calls in Messages
Assistant messages with tool calls include structured tool_calls array. Tool response messages include `tool_call_id` to match results to calls.

### Error Handling Philosophy
- API failures: Print error, continue chat loop (don't crash)
- File operations: Return error strings (agent sees and can respond)
- Memory operations: Warn to stderr, provide empty/default values

## Testing Philosophy

Tests focus on:
- Tool execution correctness (success and error cases)
- Memory save/load/compress operations
- Size calculations and thresholds

Tests intentionally don't mock the Mistral API (would need API key for integration tests). Current 18 tests cover non-API functionality.

## Common Pitfalls

1. **Don't break tool schema sync** - When modifying a tool, update function signature, registry entry, AND schema
2. **Maintain message format** - Don't modify message structure without understanding API requirements
3. **Memory threshold is KB not tokens** - Simplified for demo, production would use token counting
4. **Tool results must be strings** - Agent can't interpret other types
5. **System prompt is prepended each call** - It's not persisted in memory.json, added dynamically

## Extension Points (Phase 2 Planned)

- Rich TUI with syntax highlighting and formatted panels (not yet implemented)
- Additional tools (read_file, etc.) - follow the three-component pattern
- Alternative model selection - change `MISTRAL_MODEL` in config.py
