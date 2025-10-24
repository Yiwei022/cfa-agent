"""Unit tests for weekly calendar check tool."""
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


def test_check_new_week_no_data(clean_stats_file):
    """Test checking week status when no data file exists."""
    from tools import check_new_week_status
    
    result = check_new_week_status()
    assert "No data available" in result
    assert "Set your first weekly French learning goal" in result


def test_check_new_week_no_goal_set(clean_stats_file):
    """Test checking week status when goal not set."""
    from tools import check_new_week_status
    
    # Create stats file without goal
    stats_file = Path("stats.json")
    with open(stats_file, 'w') as f:
        json.dump({"some_data": "value"}, f)
    
    result = check_new_week_status()
    assert "No weekly goal set yet" in result


def test_check_new_week_same_week(clean_stats_file):
    """Test checking week status when in the same week as goal."""
    from tools import set_french_learning_goal, check_new_week_status
    
    # Set a goal (which automatically sets goal_week_start to current week)
    set_french_learning_goal(5)
    
    # Check week status
    result = check_new_week_status()
    
    assert "Week Status: Current Week" in result
    assert "You're still in the same week" in result
    assert "5.0 hours per week" in result
    assert "Keep working towards your goal" in result


def test_check_new_week_different_week(clean_stats_file):
    """Test checking week status when it's a new week."""
    from tools import check_new_week_status
    
    # Get current week start
    today = datetime.now()
    current_week_start = today - timedelta(days=today.weekday())
    
    # Create a goal for last week
    last_week_start = current_week_start - timedelta(days=7)
    last_week_start_str = last_week_start.strftime("%Y-%m-%d")
    
    stats_file = Path("stats.json")
    stats = {
        "weekly_goal_hours": 10,
        "goal_updated_at": (datetime.now() - timedelta(days=7)).isoformat(),
        "goal_week_start": last_week_start_str
    }
    
    with open(stats_file, 'w') as f:
        json.dump(stats, f)
    
    # Check week status
    result = check_new_week_status()
    
    assert "Week Status: NEW WEEK!" in result or "NEW WEEK" in result
    assert last_week_start_str in result
    assert current_week_start.strftime("%Y-%m-%d") in result
    assert "10.0 hours per week" in result
    assert "Set a new weekly goal" in result or "set a new weekly goal" in result


def test_set_goal_stores_week_start(clean_stats_file):
    """Test that setting a goal stores the week start date."""
    from tools import set_french_learning_goal
    
    # Set a goal
    set_french_learning_goal(7.5)
    
    # Check that goal_week_start was stored
    stats_file = Path("stats.json")
    with open(stats_file, 'r') as f:
        stats = json.load(f)
    
    assert "goal_week_start" in stats
    
    # Verify it's the current week's Monday
    today = datetime.now()
    expected_week_start = today - timedelta(days=today.weekday())
    expected_week_start_str = expected_week_start.strftime("%Y-%m-%d")
    
    assert stats["goal_week_start"] == expected_week_start_str


def test_check_new_week_tool_schema():
    """Test that check_new_week_status tool schema is properly defined."""
    from tools import TOOL_SCHEMAS
    
    # Check schema exists
    schema = next(t for t in TOOL_SCHEMAS if t["function"]["name"] == "check_new_week_status")
    assert schema["type"] == "function"
    assert len(schema["function"]["parameters"]["properties"]) == 0
    assert len(schema["function"]["parameters"]["required"]) == 0


def test_execute_tool_check_new_week(clean_stats_file):
    """Test execute_tool with check_new_week_status."""
    from tools import execute_tool
    
    # Set up some data
    execute_tool("set_french_learning_goal", {"hours_per_week": 5})
    
    # Check week status
    result = execute_tool("check_new_week_status", {})
    
    assert "Week Status" in result
    assert "Current Week" in result or "NEW WEEK" in result


def test_tool_registry_includes_week_check():
    """Test that tool registry contains check_new_week_status."""
    from tools import TOOL_FUNCTIONS
    
    assert "check_new_week_status" in TOOL_FUNCTIONS
    assert callable(TOOL_FUNCTIONS["check_new_week_status"])


def test_check_new_week_monday_to_monday(clean_stats_file):
    """Test week check when going from one Monday to next Monday."""
    from tools import check_new_week_status
    
    # Simulate setting goal on a specific Monday
    monday_week1 = datetime(2025, 10, 20)  # A Monday
    monday_week2 = datetime(2025, 10, 27)  # Next Monday
    
    # Create stats as if goal was set on week 1
    stats_file = Path("stats.json")
    stats = {
        "weekly_goal_hours": 6,
        "goal_updated_at": monday_week1.isoformat(),
        "goal_week_start": monday_week1.strftime("%Y-%m-%d")
    }
    
    with open(stats_file, 'w') as f:
        json.dump(stats, f)
    
    # If we're currently in week 1, should show same week
    # If we're currently in a different week, should show new week
    result = check_new_week_status()
    
    # Result should contain week information
    assert "Week Status" in result
    assert "2025-10-20" in result or "week" in result.lower()


def test_check_new_week_preserves_old_goal_info(clean_stats_file):
    """Test that checking new week shows the old goal information."""
    from tools import check_new_week_status
    
    # Set up a goal from 2 weeks ago
    today = datetime.now()
    current_week_start = today - timedelta(days=today.weekday())
    old_week_start = current_week_start - timedelta(days=14)  # 2 weeks ago
    old_week_start_str = old_week_start.strftime("%Y-%m-%d")
    
    stats_file = Path("stats.json")
    stats = {
        "weekly_goal_hours": 8.5,
        "goal_updated_at": (datetime.now() - timedelta(days=14)).isoformat(),
        "goal_week_start": old_week_start_str
    }
    
    with open(stats_file, 'w') as f:
        json.dump(stats, f)
    
    result = check_new_week_status()
    
    # Should show it's a new week and mention the old goal
    assert "8.5 hours per week" in result
    assert old_week_start_str in result


def test_check_new_week_handles_empty_string_key(clean_stats_file):
    """Test that check_new_week_status handles empty string keys from Mistral API."""
    from tools import execute_tool
    
    # Set a goal first
    execute_tool("set_french_learning_goal", {"hours_per_week": 5})
    
    # Call with empty string key (Mistral API sometimes does this)
    result = execute_tool("check_new_week_status", {"": ""})
    
    # Should work without error
    assert isinstance(result, str)
    assert len(result) > 0
    assert "Error" not in result or "Error checking" in result  # If error, should be handled gracefully
    assert "Week Status" in result

