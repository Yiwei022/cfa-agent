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



#. Move to OpenAI API. (Mistral overwhelmed by pdf...)
#. Enable pdf reading, time recording, ...
