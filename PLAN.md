## Design Principles
- **Simplicity First**: Few files, clear structure, easy to understand
- **Working Incrementally**: Each phase delivers a fully functional system
- **Good Practices**: Clean code without overengineering

## Plan for the next phase

### ✅ Task 1: Weekly Goal Tool (COMPLETED)
- **Tools**: `set_french_learning_goal()`, `get_french_learning_goal()`
- **Data**: Stores `weekly_goal_hours` in `stats.json`
- **Tests**: 9 unit tests in `tests/test_french_goal.py`

### ✅ Task 2: Learning Time Tracking (COMPLETED)
- **Tools**: `log_french_learning_time()`, `get_french_learning_time()`
- **Data**: Stores `learning_sessions` array in `stats.json`
- **Features**: 
  - Log individual study sessions with date
  - Automatic current week calculation (Monday to Sunday)
  - Filters old sessions
- **Tests**: 12 unit tests in `tests/test_learning_time.py`

### ✅ Task 3: Compare Goal vs Actual Time (COMPLETED)
- **Tool**: `compare_french_learning_progress()`
  - Retrieves current week's goal
  - Calculates total actual learning time for current week
  - Compares goal vs actual
  - Returns progress report with:
    - Goal hours (decimal format: 5.0 hours)
    - Actual hours (decimal format: 4.0 hours)
    - Percentage of goal achieved
    - Status with emojis (🎉 exceeded, 🟢 on track, 🟡 behind, 🔴 significantly behind)
    - Days remaining in the week
    - Motivational messages
    - Detailed session list
- **Tests**: 14 unit tests in `tests/test_progress_comparison.py` covering:
  - No goal set / No time logged
  - Behind goal / On track / Exceeded goal
  - Filtering old sessions
  - Tool schema and registry validation
  - Edge cases with decimal hours
- **Data**: Uses existing `stats.json` structure (no new fields needed)
- **Bonus**: All tools now use consistent decimal formatting (e.g., "5.0 hours", "2.5 hours")

### ✅ Task 4: Weekly Calendar Check (COMPLETED)
- **Tool**: `check_new_week_status()`
  - Checks if current week is different from the week when goal was last set
  - Returns information about:
    - Current week start date (Monday)
    - Last goal set week start date
    - Whether it's a new week
    - Friendly messages with suggestions
  - **Same week response**: Shows current goal and encourages user
  - **New week response**: Notifies user it's a new week, shows previous goal, suggests setting new goal
- **Data Updates**:
  - `set_french_learning_goal()` now stores `goal_week_start` in `stats.json`
  - This tracks which week (Monday start date) the goal belongs to
  - Enables week-to-week comparison
- **Tests**: 11 unit tests in `tests/test_week_check.py` covering:
  - Same week detection
  - New week detection  
  - No goal set / No data scenarios
  - Week rollover edge cases
  - Tool schema and registry validation
  - Empty string key handling (Mistral API compatibility)
  - Week-to-week transitions (Monday to Monday)
- **Agent Behavior**: Agent can now proactively check if it's a new week and suggest setting a new goal when appropriate


### ✅ Task 5: Move to OpenAI API (COMPLETED)
- Migrated from Mistral API to OpenAI API
- Updated agent.py, config.py, and main.py
- Changed model from `mistral-small-latest` to `gpt-5-nano`
- Updated all references and error messages
- Rich TUI implementation with beautiful terminal formatting

### ✅ Task 6: Package Deployment (COMPLETED)
- **Package Name**: `lalaby`
- **Installation Method**: pip installable with `pip install -e .`
- **Console Script**: `lalaby` command for easy access
- **Files Created**:
  - `pyproject.toml` - Modern Python packaging configuration
  - `INSTALL.md` - Comprehensive installation guide
- **Documentation**: Updated README with installation instructions
- **Testing**: Successfully installed and verified functionality
- **Clean Dependencies**: Cleaned up requirements.txt (removed duplicates)

**How to Install:**
```bash
cd /Users/davy/repo/cfa-agent
pip install -e .
python3 main.py  # or lalaby (if Python bin in PATH)
```

## Next Task

### 🎯 Task 7: PDF Reading Support (PLANNED)
- **Library**: `pypdf` (already installed in requirements.txt)
- **Tool**: `read_pdf(filename: str) -> str`
  - Extract text content from PDF files
  - Support for French learning materials
  - Handle multi-page documents
- **Use case**: Users can upload French texts, articles, or lessons in PDF format
- **Tests**: Unit tests in `tests/test_pdf_reading.py`


