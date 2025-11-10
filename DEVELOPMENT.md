# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a pedagogical demonstration of AI agents with function calling using OpenAI's Responses API. It's a simple agentic CLI chatbot built for the PGE3-EN Coding for AI course at Aivancity (2025-2026). The codebase is intentionally minimal to demonstrate core agentic concepts clearly.

## Development Commands

### Setup
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# OR .venv\Scripts\activate  # Windows
pip install -r requirements.txt
echo "OPENAI_API_KEY=your-key" > .env
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
The agent uses OpenAI's Responses API with stateful conversation management:

1. User sends message → Sent to Responses API with previous_response_id
2. **Responses API call**: Stateful context maintained server-side via response IDs
3. API decides whether to call tools based on instructions and conversation state
4. If tools called: Execute Python functions locally, display results
5. Response includes tool outputs and final message
6. Store response.id for next conversation turn

This single-call pattern with server-side state management is the key feature of the Responses API.

### File Responsibilities

- **[main.py](main.py)** - CLI chat loop, command handling (`/exit`, `/clear`, `/help`, `/reset`), saves local message history, resets conversation state
- **[agent.py](agent.py)** - OpenAI Responses API integration, stateful conversation tracking via response IDs, tool execution
- **[tools.py](tools.py)** - Tool implementations (Python functions), tool schemas (JSON), tool registry (dict mapping names to functions), execution dispatcher
- **[memory.py](memory.py)** - Local JSON persistence for display purposes (actual state managed by Responses API server-side)
- **[config.py](config.py)** - Environment variables, model selection (`gpt-5-mini`)
- **[prompts.yaml](prompts.yaml)** - System prompt (agent behavior) passed as instructions to Responses API

### Memory Management Strategy

With the Responses API, memory management is handled server-side:
1. **Stateful by default**: API tracks full conversation history via `previous_response_id`
2. **No manual summarization needed**: Context window managed automatically by OpenAI
3. **Local message history**: Kept in `memory.json` for display and logging purposes only
4. **Reset conversation**: Use `/clear` command to reset `last_response_id` and start fresh

Why this matters: The Responses API eliminates the complexity of manual memory management. The server maintains state, and you simply pass the previous response ID to continue the conversation.

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

Tests intentionally don't mock the OpenAI Responses API (would need API key for integration tests). Current tests cover non-API functionality.

## Common Pitfalls

1. **Don't break tool schema sync** - When modifying a tool, update function signature, registry entry, AND schema
2. **Response ID is critical** - Always store and pass `previous_response_id` to maintain conversation state
3. **Local vs API state** - Local `messages` array is for display only; actual state is server-side
4. **Tool results must be strings** - Agent can't interpret other types
5. **System prompt as instructions** - Passed as `instructions` parameter, not in messages array
6. **Reset conversation properly** - Clear both local messages AND `last_response_id` when resetting

## Extension Points (Phase 2 Planned)

- Rich TUI with syntax highlighting and formatted panels (already implemented)
- Additional tools (read_file, etc.) - follow the three-component pattern
- Alternative model selection - change `OPENAI_MODEL` in config.py
