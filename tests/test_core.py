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
    from config import MISTRAL_MODEL, MEMORY_THRESHOLD_KB, MEMORY_KEEP_LAST_N

    assert MISTRAL_MODEL == "mistral-small-latest"
    assert MEMORY_THRESHOLD_KB == 50
    assert MEMORY_KEEP_LAST_N == 10


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
    from tools import TOOL_SCHEMAS



    # Check write_to_file schema
    write_schema = next(t for t in TOOL_SCHEMAS if t["function"]["name"] == "write_to_file")
    assert write_schema["type"] == "function"
    assert "filename" in write_schema["function"]["parameters"]["properties"]
    assert "content" in write_schema["function"]["parameters"]["properties"]

    # Check get_date schema
    date_schema = next(t for t in TOOL_SCHEMAS if t["function"]["name"] == "get_date")
    assert date_schema["type"] == "function"
    assert len(date_schema["function"]["parameters"]["properties"]) == 0


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


def test_execute_tool_empty_string_key():
    """Test execute_tool handles empty string keys from Mistral API."""
    from tools import execute_tool

    # Mistral API sometimes sends {"": ""} for tools with no parameters
    result = execute_tool("get_date", {"": ""})
    
    # Should work without error
    assert isinstance(result, str)
    assert len(result) > 0
    assert "Error" not in result


def test_tool_registry():
    """Test that tool registry contains all tools."""
    from tools import TOOL_FUNCTIONS

    assert "write_to_file" in TOOL_FUNCTIONS
    assert "get_date" in TOOL_FUNCTIONS
    assert callable(TOOL_FUNCTIONS["write_to_file"])
    assert callable(TOOL_FUNCTIONS["get_date"])
