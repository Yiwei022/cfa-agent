"""Unit tests for core components."""
import pytest
from pathlib import Path
from datetime import datetime
import yaml

# Test config.py
def test_config_paths():
    """Test that config paths are correctly defined."""
    from config import PROJECT_DIR, MEMORY_FILE, PROMPTS_FILE

    assert PROJECT_DIR.exists()
    assert PROMPTS_FILE.exists()
    assert PROMPTS_FILE.name == "prompts.yaml"
    assert MEMORY_FILE.name == "memory.json"


def test_load_prompts():
    """Test loading prompts from YAML file."""
    from config import load_prompts

    prompts = load_prompts()
    assert "system_prompt" in prompts
    assert "summarization_prompt" in prompts
    assert len(prompts["system_prompt"]) > 0
    assert "tools" in prompts["system_prompt"].lower()


def test_config_constants():
    """Test configuration constants."""
    from config import (
        MISTRAL_MODEL,
        MEMORY_THRESHOLD_KB,
        MEMORY_KEEP_LAST_N,
        MAX_TOOL_ROUNDS,
        MISTRAL_RATE_LIMIT_RPS,
        MISTRAL_MIN_DELAY
    )

    # Verify model
    assert isinstance(MISTRAL_MODEL, str)
    assert MISTRAL_MODEL == "mistral-small-latest"

    # Verify memory thresholds (Phase 3 values)
    assert isinstance(MEMORY_THRESHOLD_KB, (int, float))
    assert MEMORY_THRESHOLD_KB == 20  # Phase 3 default

    assert isinstance(MEMORY_KEEP_LAST_N, int)
    assert MEMORY_KEEP_LAST_N == 5  # Phase 3 default

    # Verify tool calling limit (Phase 3)
    assert isinstance(MAX_TOOL_ROUNDS, int)
    assert MAX_TOOL_ROUNDS == 5  # Phase 3 default

    # Verify rate limiting constants (Phase 3)
    assert isinstance(MISTRAL_RATE_LIMIT_RPS, (int, float))
    assert MISTRAL_RATE_LIMIT_RPS == 1.0  # Free tier

    assert isinstance(MISTRAL_MIN_DELAY, (int, float))
    assert MISTRAL_MIN_DELAY == 1.0  # 1 second for free tier


# Test tools.py
def test_get_date():
    """Test get_date tool returns a valid date string."""
    from tools import get_date

    date_str = get_date()
    assert isinstance(date_str, str)
    assert len(date_str) > 0
    # Should contain current year
    current_year = str(datetime.now().year)
    assert current_year in date_str


def test_write_to_file():
    """Test write_to_file tool."""
    from tools import write_to_file

    test_file = "test_temp_file.txt"
    test_content = "Test content for unit test"

    # Write file
    result = write_to_file(test_file, test_content)
    assert "Successfully" in result
    assert test_file in result

    # Verify file was created and contains correct content
    filepath = Path(test_file)
    assert filepath.exists()
    assert filepath.read_text() == test_content

    # Cleanup
    filepath.unlink()


def test_tool_schemas():
    """Test that tool schemas are properly defined."""
    from tools import TOOL_SCHEMAS, TOOL_FUNCTIONS

    # Verify we have all 6 tools (Phase 3)
    assert len(TOOL_SCHEMAS) == 6

    # Verify all schemas have required structure
    for schema in TOOL_SCHEMAS:
        assert schema["type"] == "function"
        assert "name" in schema["function"]
        assert "description" in schema["function"]
        assert "parameters" in schema["function"]

    # Verify all tool names in schemas match registry
    schema_names = {schema["function"]["name"] for schema in TOOL_SCHEMAS}
    registry_names = set(TOOL_FUNCTIONS.keys())
    assert schema_names == registry_names, f"Schema names {schema_names} don't match registry {registry_names}"

    # Check write_to_file schema
    write_schema = next(t for t in TOOL_SCHEMAS if t["function"]["name"] == "write_to_file")
    assert write_schema["type"] == "function"
    assert "filename" in write_schema["function"]["parameters"]["properties"]
    assert "content" in write_schema["function"]["parameters"]["properties"]

    # Check get_date schema
    date_schema = next(t for t in TOOL_SCHEMAS if t["function"]["name"] == "get_date")
    assert date_schema["type"] == "function"


def test_execute_tool_get_date():
    """Test execute_tool with get_date."""
    from tools import execute_tool

    result = execute_tool("get_date", {})
    assert isinstance(result, str)
    assert len(result) > 0


def test_execute_tool_write_to_file():
    """Test execute_tool with write_to_file."""
    from tools import execute_tool

    test_file = "test_execute_tool.txt"
    result = execute_tool("write_to_file", {
        "filename": test_file,
        "content": "Execute tool test"
    })

    assert "Successfully" in result

    # Cleanup
    Path(test_file).unlink()


def test_execute_tool_unknown():
    """Test execute_tool with unknown tool name."""
    from tools import execute_tool

    result = execute_tool("unknown_tool", {})
    assert "Error" in result
    assert "Unknown tool" in result


def test_tool_registry():
    """Test that tool registry contains all tools."""
    from tools import TOOL_FUNCTIONS

    # Phase 3 has 6 tools
    expected_tools = [
        "write_to_file",
        "read_file",
        "get_date",
        "get_batch_newsletter",
        "list_files",
        "curl_read"
    ]

    # Verify all expected tools are in registry
    for tool_name in expected_tools:
        assert tool_name in TOOL_FUNCTIONS, f"Tool {tool_name} not in registry"
        assert callable(TOOL_FUNCTIONS[tool_name]), f"Tool {tool_name} is not callable"

    # Verify registry has exactly the expected tools
    assert len(TOOL_FUNCTIONS) == len(expected_tools), \
        f"Expected {len(expected_tools)} tools, found {len(TOOL_FUNCTIONS)}"
