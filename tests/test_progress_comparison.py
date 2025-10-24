"""Unit tests for French learning progress comparison tool."""
import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta


@pytest.fixture
def clean_stats_file():
    """Fixture to clean up stats.json before and after tests."""
    stats_file = Path("stats.json")
    # Clean up before test
    if stats_file.exists():
        stats_file.unlink()
    
    yield
    
    # Clean up after test
    if stats_file.exists():
        stats_file.unlink()


def test_compare_progress_no_data(clean_stats_file):
    """Test comparing progress when no data file exists."""
    from tools import compare_french_learning_progress
    
    result = compare_french_learning_progress()
    assert "No data available" in result
    assert "set a weekly goal" in result


def test_compare_progress_no_goal_set(clean_stats_file):
    """Test comparing progress when no goal is set."""
    from tools import compare_french_learning_progress, log_french_learning_time
    
    # Log some time without setting a goal
    log_french_learning_time(2)
    
    result = compare_french_learning_progress()
    assert "No weekly goal set yet" in result
    assert "Please set a goal first" in result


def test_compare_progress_no_time_logged(clean_stats_file):
    """Test comparing progress when goal is set but no time logged."""
    from tools import compare_french_learning_progress, set_french_learning_goal
    
    # Set goal but don't log any time
    set_french_learning_goal(5)
    
    result = compare_french_learning_progress()
    
    assert "Progress Report" in result
    assert "Weekly Goal: 5.0 hours" in result
    assert "Actual Time: 0.0 hours" in result
    assert "0.0%" in result
    assert "Significantly behind" in result or "behind" in result.lower()
    assert "No sessions logged this week yet" in result


def test_compare_progress_behind_goal(clean_stats_file):
    """Test comparing progress when behind the goal."""
    from tools import compare_french_learning_progress, set_french_learning_goal, log_french_learning_time
    
    # Set goal to 10 hours
    set_french_learning_goal(10)
    
    # Get current week's Monday
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    
    # Log only 3 hours (30%)
    date1 = week_start.strftime("%Y-%m-%d")
    date2 = (week_start + timedelta(days=1)).strftime("%Y-%m-%d")
    log_french_learning_time(1.5, date=date1)
    log_french_learning_time(1.5, date=date2)
    
    result = compare_french_learning_progress()
    
    assert "Progress Report" in result
    assert "Weekly Goal: 10.0 hours" in result
    assert "Actual Time: 3.0 hours" in result
    assert "30.0%" in result
    assert "behind" in result.lower()
    assert "You need" in result and "more hours" in result


def test_compare_progress_on_track(clean_stats_file):
    """Test comparing progress when on track with goal."""
    from tools import compare_french_learning_progress, set_french_learning_goal, log_french_learning_time
    
    # Set goal to 5 hours
    set_french_learning_goal(5)
    
    # Get current week's Monday
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    
    # Log 4 hours (80%)
    date1 = week_start.strftime("%Y-%m-%d")
    date2 = (week_start + timedelta(days=1)).strftime("%Y-%m-%d")
    log_french_learning_time(2, date=date1)
    log_french_learning_time(2, date=date2)
    
    result = compare_french_learning_progress()
    
    assert "Progress Report" in result
    assert "Weekly Goal: 5.0 hours" in result
    assert "Actual Time: 4.0 hours" in result
    assert "80.0%" in result
    assert "On track" in result
    assert "🟢" in result or "👍" in result


def test_compare_progress_goal_exceeded(clean_stats_file):
    """Test comparing progress when goal is exceeded."""
    from tools import compare_french_learning_progress, set_french_learning_goal, log_french_learning_time
    
    # Set goal to 5 hours
    set_french_learning_goal(5)
    
    # Get current week's Monday
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    
    # Log 6 hours (120%)
    date1 = week_start.strftime("%Y-%m-%d")
    date2 = (week_start + timedelta(days=1)).strftime("%Y-%m-%d")
    log_french_learning_time(3, date=date1)
    log_french_learning_time(3, date=date2)
    
    result = compare_french_learning_progress()
    
    assert "Progress Report" in result
    assert "Weekly Goal: 5.0 hours" in result
    assert "Actual Time: 6.0 hours" in result
    assert "120.0%" in result
    assert "exceeded" in result.lower()
    assert "Amazing work" in result or "🌟" in result


def test_compare_progress_exactly_met(clean_stats_file):
    """Test comparing progress when goal is exactly met."""
    from tools import compare_french_learning_progress, set_french_learning_goal, log_french_learning_time
    
    # Set goal to 5 hours
    set_french_learning_goal(5)
    
    # Get current week's Monday
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    
    # Log exactly 5 hours (100%)
    date1 = week_start.strftime("%Y-%m-%d")
    log_french_learning_time(5, date=date1)
    
    result = compare_french_learning_progress()
    
    assert "Progress Report" in result
    assert "Weekly Goal: 5.0 hours" in result
    assert "Actual Time: 5.0 hours" in result
    assert "100.0%" in result
    assert "exceeded" in result.lower() or "Goal exceeded" in result


def test_compare_progress_filters_old_sessions(clean_stats_file):
    """Test that progress comparison only counts current week's sessions."""
    from tools import compare_french_learning_progress, set_french_learning_goal, log_french_learning_time
    
    # Set goal to 5 hours
    set_french_learning_goal(5)
    
    # Get current week's Monday
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    
    # Log old session (last month) - should not be counted
    old_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    log_french_learning_time(10, date=old_date)
    
    # Log current week session
    current_date = week_start.strftime("%Y-%m-%d")
    log_french_learning_time(2, date=current_date)
    
    result = compare_french_learning_progress()
    
    # Should only count the 2 hours from this week, not the 10 from last month
    assert "Actual Time: 2.0 hours" in result
    assert "40.0%" in result
    assert old_date not in result
    assert current_date in result


def test_compare_progress_shows_days_remaining(clean_stats_file):
    """Test that progress report shows days remaining in the week."""
    from tools import compare_french_learning_progress, set_french_learning_goal, log_french_learning_time
    
    # Set goal
    set_french_learning_goal(5)
    
    # Log some time
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    log_french_learning_time(2, date=week_start.strftime("%Y-%m-%d"))
    
    result = compare_french_learning_progress()
    
    # Should show days remaining
    assert "Days Remaining:" in result
    assert "day(s)" in result


def test_compare_progress_shows_sessions_list(clean_stats_file):
    """Test that progress report lists individual sessions."""
    from tools import compare_french_learning_progress, set_french_learning_goal, log_french_learning_time
    
    # Set goal
    set_french_learning_goal(5)
    
    # Get current week dates
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    date1 = week_start.strftime("%Y-%m-%d")
    date2 = (week_start + timedelta(days=1)).strftime("%Y-%m-%d")
    date3 = (week_start + timedelta(days=2)).strftime("%Y-%m-%d")
    
    # Log multiple sessions
    log_french_learning_time(1, date=date1)
    log_french_learning_time(1.5, date=date2)
    log_french_learning_time(0.5, date=date3)
    
    result = compare_french_learning_progress()
    
    # Should list all sessions
    assert "Sessions this week:" in result
    assert date1 in result and "1.0 hours" in result
    assert date2 in result and "1.5 hours" in result
    assert date3 in result and "0.5 hours" in result


def test_compare_progress_tool_schema():
    """Test that compare_french_learning_progress tool schema is properly defined."""
    from tools import TOOL_SCHEMAS
    
    # Check schema exists
    schema = next(t for t in TOOL_SCHEMAS if t["function"]["name"] == "compare_french_learning_progress")
    assert schema["type"] == "function"
    assert len(schema["function"]["parameters"]["properties"]) == 0
    assert len(schema["function"]["parameters"]["required"]) == 0


def test_execute_tool_compare_progress(clean_stats_file):
    """Test execute_tool with compare_french_learning_progress."""
    from tools import execute_tool
    
    # Set up some data
    execute_tool("set_french_learning_goal", {"hours_per_week": 5})
    execute_tool("log_french_learning_time", {"hours": 3})
    
    # Compare progress
    result = execute_tool("compare_french_learning_progress", {})
    
    assert "Progress Report" in result
    assert "5.0 hours" in result
    assert "3.0 hours" in result


def test_tool_registry_includes_compare_progress():
    """Test that tool registry contains compare_french_learning_progress."""
    from tools import TOOL_FUNCTIONS
    
    assert "compare_french_learning_progress" in TOOL_FUNCTIONS
    assert callable(TOOL_FUNCTIONS["compare_french_learning_progress"])


def test_compare_progress_with_decimal_hours(clean_stats_file):
    """Test progress comparison with decimal hour values."""
    from tools import compare_french_learning_progress, set_french_learning_goal, log_french_learning_time
    
    # Set goal with decimal
    set_french_learning_goal(7.5)
    
    # Get current week
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    
    # Log decimal hours
    log_french_learning_time(2.25, date=week_start.strftime("%Y-%m-%d"))
    log_french_learning_time(1.75, date=(week_start + timedelta(days=1)).strftime("%Y-%m-%d"))
    
    result = compare_french_learning_progress()
    
    assert "Weekly Goal: 7.5 hours" in result
    assert "Actual Time: 4.0 hours" in result
    # 4/7.5 = 53.33%
    assert "53.3%" in result

