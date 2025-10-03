# Project Plan: Simple Agentic CLI Chatbot

A pedagogical demonstration of Mistral API with agentic function calling capabilities.

## Design Principles
- **Simplicity First**: Few files, clear structure, easy to understand
- **Working Incrementally**: Each phase delivers a fully functional system
- **Good Practices**: Clean code without overengineering
- **Pedagogical**: Code should clearly demonstrate agentic concepts

## Current Status

**✅ Phase 1: COMPLETE** - Fully functional agentic chatbot with tool calling and memory management
**⏳ Phase 2: PENDING** - Enhanced UX with Rich TUI and documentation

## Architecture Overview (Implemented File Structure)
```
cfa/
├── main.py          # ✅ CLI entry point and chat loop
├── agent.py         # ✅ Mistral API integration and agent logic
├── tools.py         # ✅ Tool definitions (write_to_file, get_date)
├── memory.py        # ✅ Simple JSON-based context management
├── config.py        # ✅ Configuration and environment management
├── prompts.yaml     # ✅ System and summarization prompts
├── .env             # ✅ API key configuration (not in git)
├── memory.json      # ✅ Auto-generated conversation history
├── README.md        # ✅ Comprehensive educational guide
└── tests/           # ✅ Unit tests (18 tests, all passing)
    ├── test_core.py
    └── test_memory.py
```

## Phase 1: Simple Working Version ✓ Core Deliverable
**Goal**: Deliver a fully functional agentic chatbot demonstrating all key concepts

### Components to Build:
1. **Project Setup** ✅
   - ~~Initialize `pyproject.toml` with minimal dependencies: `typer`, `mistralai`~~ (using direct pip install)
   - ✅ Create simple project structure (no complex packaging yet)

2. **CLI Chat Loop** (`main.py`) ✅
   - ✅ Simple line-by-line chat interface (no `rich` TUI yet)
   - ✅ Basic command handling (exit, clear, help)
   - ✅ Load memory on startup, save on exit

3. **Mistral API Integration** (`agent.py`) ✅
   - ✅ Connect to Mistral API with function calling support
   - ✅ System prompt for agentic behavior
   - ✅ Tool call parsing and execution loop
   - ✅ Return formatted responses to user

4. **Tool System** (`tools.py`) ✅
   - ✅ Define tool schema compatible with Mistral API
   - ✅ Implement two demonstration tools:
     - ✅ `write_to_file(filename, content)`: Write content to a file
     - ✅ `get_date()`: Return today's date in readable format
   - ✅ Tool registry and dispatcher

5. **Memory Management** (`memory.py`) ✅
   - ✅ Save conversation history as JSON in project folder
   - ✅ Load existing history on startup
   - ✅ Append new messages (user, assistant, tool calls)
   - ✅ **Context management logic**:
     - ✅ Check total memory size in KB before each turn
     - ✅ If above threshold (e.g., 50KB), call Mistral to summarize conversation
     - ✅ Keep last N messages + summary, discard old details
     - ✅ Continue conversation with compressed context

6. **Configuration** (`config.py`) ✅
   - ✅ API key management (from `.env` file using python-dotenv)
   - ✅ Memory thresholds and limits
   - ✅ Model selection and parameters
   - ✅ Prompts loaded from `prompts.yaml`

7. **Error Handling & Testing** ✅
   - ✅ Basic error handling for API failures and file operations
   - ✅ Simple unit tests (`pytest`) for core functions:
     - ✅ Tool execution (10 tests)
     - ✅ Memory save/load (8 tests)
     - ✅ All 18 tests passing
   - ✅ Basic logging for debugging

### End of Phase 1 Milestone: ✅ COMPLETED
✅ User can chat with agent → agent can call tools → memory persists and auto-summarizes → tested and working → complete demo

**Phase 1 Complete!** All core functionality implemented and tested. See [README.md](README.md) for comprehensive documentation.

## Phase 2: Enhanced UX & Documentation
**Goal**: Polish the experience and make it shareable

- Integrate `rich` library for beautiful TUI:
  - Syntax highlighting for code
  - Formatted panels for agent responses
  - Spinner during API calls
  - Colorized tool call notifications
- Add one more useful tool:
  - `read_file(filename)` to demonstrate multi-tool workflows
- Comprehensive README with:
  - Quick start guide
  - Architecture explanation
  - How to add new tools
  - Example conversation screenshots
- Package for easy installation (`pip install -e .`)

