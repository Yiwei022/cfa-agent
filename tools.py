"""Tool definitions and execution for the agentic chatbot."""
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict


# Tool implementations

def write_to_file(filename: str, content: str) -> str:
    """Write content to a file.

    Args:
        filename: Name of the file to write to
        content: Content to write to the file

    Returns:
        Success message or error description
    """
    try:
        filepath = Path(filename)
        filepath.write_text(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Error writing to file: {str(e)}"


def get_date() -> str:
    """Get today's date in a readable format.

    Returns:
        Today's date as a formatted string
    """
    return datetime.now().strftime("%A, %B %d, %Y")


# Tool registry mapping tool names to functions
TOOL_FUNCTIONS: Dict[str, Callable] = {
    "write_to_file": write_to_file,
    "get_date": get_date,
}


# Tool schemas for Mistral API (following OpenAI function calling format)
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "write_to_file",
            "description": "Write content to a file in the current directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The name of the file to write to"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file"
                    }
                },
                "required": ["filename", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_date",
            "description": "Get today's date in a readable format",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> str:
    """Execute a tool by name with given arguments.

    Args:
        tool_name: Name of the tool to execute
        tool_args: Dictionary of arguments to pass to the tool

    Returns:
        Result of the tool execution as a string
    """
    if tool_name not in TOOL_FUNCTIONS:
        return f"Error: Unknown tool '{tool_name}'"

    try:
        tool_func = TOOL_FUNCTIONS[tool_name]
        result = tool_func(**tool_args)
        return str(result)
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"
