"""Unit tests for French learning goal tools."""
import pytest
import json
from pathlib import Path
from datetime import datetime


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


def test_set_french_learning_goal(clean_stats_file):
    """Test setting a French learning goal."""
    from tools import set_french_learning_goal
    
    # Set goal to 5 hours per week
    result = set_french_learning_goal(5)
    
    # Check success message
    assert "✓" in result
    assert "5" in result
    assert "hours per week" in result
    
    # Verify file was created
    stats_file = Path("stats.json")
    assert stats_file.exists()
    
    # Verify content
    with open(stats_file, 'r') as f:
        stats = json.load(f)
    
    assert stats["weekly_goal_hours"] == 5
    assert "goal_updated_at" in stats
    # Verify timestamp is valid ISO format
    datetime.fromisoformat(stats["goal_updated_at"])


def test_set_french_learning_goal_update(clean_stats_file):
    """Test updating an existing French learning goal."""
    from tools import set_french_learning_goal
    
    # Set initial goal
    set_french_learning_goal(3)
    
    # Update goal
    result = set_french_learning_goal(7)
    assert "7" in result
    
    # Verify updated content
    stats_file = Path("stats.json")
    with open(stats_file, 'r') as f:
        stats = json.load(f)
    
    assert stats["weekly_goal_hours"] == 7


def test_get_french_learning_goal_not_set(clean_stats_file):
    """Test getting goal when no goal is set."""
    from tools import get_french_learning_goal
    
    result = get_french_learning_goal()
    assert "No French learning goal set yet" in result


def test_get_french_learning_goal_set(clean_stats_file):
    """Test getting an existing French learning goal."""
    from tools import set_french_learning_goal, get_french_learning_goal
    
    # Set goal first
    set_french_learning_goal(4.5)
    
    # Get goal
    result = get_french_learning_goal()
    
    assert "4.5" in result
    assert "hours per week" in result
    assert "Updated:" in result


def test_french_goal_tool_schemas():
    """Test that French goal tool schemas are properly defined."""
    from tools import TOOL_SCHEMAS
    
    # Check set_french_learning_goal schema
    set_schema = next(t for t in TOOL_SCHEMAS if t["function"]["name"] == "set_french_learning_goal")
    assert set_schema["type"] == "function"
    assert "hours_per_week" in set_schema["function"]["parameters"]["properties"]
    assert set_schema["function"]["parameters"]["properties"]["hours_per_week"]["type"] == "number"
    assert "hours_per_week" in set_schema["function"]["parameters"]["required"]
    
    # Check get_french_learning_goal schema
    get_schema = next(t for t in TOOL_SCHEMAS if t["function"]["name"] == "get_french_learning_goal")
    assert get_schema["type"] == "function"
    assert len(get_schema["function"]["parameters"]["properties"]) == 0


def test_execute_tool_set_french_goal(clean_stats_file):
    """Test execute_tool with set_french_learning_goal."""
    from tools import execute_tool
    
    result = execute_tool("set_french_learning_goal", {"hours_per_week": 6})
    
    assert "✓" in result
    assert "6" in result
    
    # Verify file exists
    assert Path("stats.json").exists()


def test_execute_tool_get_french_goal(clean_stats_file):
    """Test execute_tool with get_french_learning_goal."""
    from tools import execute_tool
    
    # Set goal first
    execute_tool("set_french_learning_goal", {"hours_per_week": 8})
    
    # Get goal
    result = execute_tool("get_french_learning_goal", {})
    
    assert "8" in result
    assert "hours per week" in result


def test_tool_registry_includes_french_goal():
    """Test that tool registry contains French goal tools."""
    from tools import TOOL_FUNCTIONS
    
    assert "set_french_learning_goal" in TOOL_FUNCTIONS
    assert "get_french_learning_goal" in TOOL_FUNCTIONS
    assert callable(TOOL_FUNCTIONS["set_french_learning_goal"])
    assert callable(TOOL_FUNCTIONS["get_french_learning_goal"])


def test_stats_json_preserves_other_data(clean_stats_file):
    """Test that stats.json preserves other data when updating goal."""
    from tools import set_french_learning_goal
    
    # Manually create stats with additional data
    stats_file = Path("stats.json")
    initial_stats = {
        "weekly_goal_hours": 5,
        "goal_updated_at": "2025-01-01T00:00:00",
        "some_future_field": "future data"
    }
    
    with open(stats_file, 'w') as f:
        json.dump(initial_stats, f)
    
    # Update goal
    set_french_learning_goal(10)
    
    # Verify other data is preserved
    with open(stats_file, 'r') as f:
        stats = json.load(f)
    
    assert stats["weekly_goal_hours"] == 10
    assert stats["some_future_field"] == "future data"

