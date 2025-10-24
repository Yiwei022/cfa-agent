"""Unit tests for French learning time tracking tools."""
import pytest
import json
import os
from pathlib import Path
from datetime import datetime, timedelta


@pytest.fixture
def clean_stats_file(tmp_path, monkeypatch):
    """Fixture to run tests in a temporary directory to avoid deleting real stats.json."""
    # Change to temporary directory for the test
    monkeypatch.chdir(tmp_path)
    yield
    # Tests run in tmp_path, so real stats.json is never touched


def test_log_french_learning_time_today(clean_stats_file):
    """Test logging French learning time for today."""
    from tools import log_french_learning_time
    
    # Log 2 hours of learning today
    result = log_french_learning_time(2)
    
    # Check success message
    assert "✓" in result
    assert "2" in result
    assert "hours" in result
    
    # Verify file was created
    stats_file = Path("stats.json")
    assert stats_file.exists()
    
    # Verify content
    with open(stats_file, 'r') as f:
        stats = json.load(f)
    
    assert "learning_sessions" in stats
    assert len(stats["learning_sessions"]) == 1
    
    session = stats["learning_sessions"][0]
    assert session["hours"] == 2
    assert session["date"] == datetime.now().strftime("%Y-%m-%d")
    assert "logged_at" in session


def test_log_french_learning_time_specific_date(clean_stats_file):
    """Test logging French learning time for a specific date."""
    from tools import log_french_learning_time
    
    # Log 1.5 hours for a specific date
    test_date = "2025-10-20"
    result = log_french_learning_time(1.5, date=test_date)
    
    assert "1.5" in result
    assert test_date in result
    
    # Verify content
    stats_file = Path("stats.json")
    with open(stats_file, 'r') as f:
        stats = json.load(f)
    
    session = stats["learning_sessions"][0]
    assert session["hours"] == 1.5
    assert session["date"] == test_date


def test_log_multiple_sessions(clean_stats_file):
    """Test logging multiple learning sessions."""
    from tools import log_french_learning_time
    
    # Log multiple sessions
    log_french_learning_time(1, date="2025-10-21")
    log_french_learning_time(2, date="2025-10-22")
    log_french_learning_time(0.5, date="2025-10-23")
    
    # Verify all sessions are stored
    stats_file = Path("stats.json")
    with open(stats_file, 'r') as f:
        stats = json.load(f)
    
    assert len(stats["learning_sessions"]) == 3
    assert stats["learning_sessions"][0]["hours"] == 1
    assert stats["learning_sessions"][1]["hours"] == 2
    assert stats["learning_sessions"][2]["hours"] == 0.5


def test_get_french_learning_time_not_logged(clean_stats_file):
    """Test getting learning time when nothing is logged."""
    from tools import get_french_learning_time
    
    result = get_french_learning_time()
    assert "No learning time logged yet" in result


def test_get_french_learning_time_current_week(clean_stats_file):
    """Test getting learning time for the current week."""
    from tools import log_french_learning_time, get_french_learning_time
    
    # Get current week's Monday
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    
    # Log sessions for this week
    date1 = week_start.strftime("%Y-%m-%d")
    date2 = (week_start + timedelta(days=2)).strftime("%Y-%m-%d")
    
    log_french_learning_time(1.5, date=date1)
    log_french_learning_time(2, date=date2)
    
    # Get learning time
    result = get_french_learning_time()
    
    assert "This week's French learning time" in result
    assert "Total: 3.5 hours" in result
    assert date1 in result
    assert date2 in result
    assert "1.5 hours" in result
    assert "2.0 hours" in result


def test_get_french_learning_time_filters_old_sessions(clean_stats_file):
    """Test that get_french_learning_time only shows current week."""
    from tools import log_french_learning_time, get_french_learning_time
    
    # Get current week's Monday
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    
    # Log old session (last month)
    old_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    log_french_learning_time(5, date=old_date)
    
    # Log current week session
    current_date = week_start.strftime("%Y-%m-%d")
    log_french_learning_time(2, date=current_date)
    
    # Get learning time - should only show current week
    result = get_french_learning_time()
    
    assert "Total: 2.0 hours" in result
    assert current_date in result
    assert old_date not in result


def test_learning_time_tool_schemas():
    """Test that learning time tool schemas are properly defined."""
    from tools import TOOL_SCHEMAS
    
    # Check log_french_learning_time schema
    log_schema = next(t for t in TOOL_SCHEMAS if t["function"]["name"] == "log_french_learning_time")
    assert log_schema["type"] == "function"
    assert "hours" in log_schema["function"]["parameters"]["properties"]
    assert "date" in log_schema["function"]["parameters"]["properties"]
    assert log_schema["function"]["parameters"]["properties"]["hours"]["type"] == "number"
    assert log_schema["function"]["parameters"]["properties"]["date"]["type"] == "string"
    assert "hours" in log_schema["function"]["parameters"]["required"]
    assert "date" not in log_schema["function"]["parameters"]["required"]  # optional
    
    # Check get_french_learning_time schema
    get_schema = next(t for t in TOOL_SCHEMAS if t["function"]["name"] == "get_french_learning_time")
    assert get_schema["type"] == "function"
    assert len(get_schema["function"]["parameters"]["properties"]) == 0


def test_execute_tool_log_learning_time(clean_stats_file):
    """Test execute_tool with log_french_learning_time."""
    from tools import execute_tool
    
    result = execute_tool("log_french_learning_time", {"hours": 3})
    
    assert "✓" in result
    assert "3" in result
    
    # Verify file exists
    assert Path("stats.json").exists()


def test_execute_tool_get_learning_time(clean_stats_file):
    """Test execute_tool with get_french_learning_time."""
    from tools import execute_tool
    
    # Log some time first
    execute_tool("log_french_learning_time", {"hours": 2.5})
    
    # Get learning time
    result = execute_tool("get_french_learning_time", {})
    
    assert "2.5 hours" in result
    assert "This week's French learning time" in result


def test_tool_registry_includes_learning_time():
    """Test that tool registry contains learning time tools."""
    from tools import TOOL_FUNCTIONS
    
    assert "log_french_learning_time" in TOOL_FUNCTIONS
    assert "get_french_learning_time" in TOOL_FUNCTIONS
    assert callable(TOOL_FUNCTIONS["log_french_learning_time"])
    assert callable(TOOL_FUNCTIONS["get_french_learning_time"])


def test_learning_sessions_preserve_goal_data(clean_stats_file):
    """Test that logging learning time preserves goal data."""
    from tools import set_french_learning_goal, log_french_learning_time
    
    # Set a goal first
    set_french_learning_goal(5)
    
    # Log learning time
    log_french_learning_time(2)
    
    # Verify both are preserved
    stats_file = Path("stats.json")
    with open(stats_file, 'r') as f:
        stats = json.load(f)
    
    assert stats["weekly_goal_hours"] == 5
    assert "goal_updated_at" in stats
    assert len(stats["learning_sessions"]) == 1
    assert stats["learning_sessions"][0]["hours"] == 2


def test_get_french_learning_time_no_current_week(clean_stats_file):
    """Test getting learning time when there are old sessions but none this week."""
    from tools import log_french_learning_time, get_french_learning_time
    
    # Log old session (last month)
    today = datetime.now()
    old_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    log_french_learning_time(5, date=old_date)
    
    # Get learning time - should show message about no sessions this week
    result = get_french_learning_time()
    
    assert "No learning time logged this week yet" in result
    week_start = today - timedelta(days=today.weekday())
    assert week_start.strftime("%Y-%m-%d") in result

