"""Tool definitions and execution for the agentic chatbot."""
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict
import requests
from bs4 import BeautifulSoup
import json


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

def get_batch_newsletter() -> str:
    """Scrape the latest AI news headlines from The Batch newsletter.

    Returns:
        Latest headlines from deeplearning.ai's The Batch as a formatted string
    """
    url = "https://www.deeplearning.ai/the-batch/"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        headlines = []

        # Find article headlines - adjust selectors based on actual page structure
        articles = soup.find_all(['h2', 'h3', 'h4'], class_=lambda x: x and ('headline' in x.lower() or 'title' in x.lower()))

        if not articles:
            # Fallback: try to find common heading tags
            articles = soup.find_all(['h2', 'h3'], limit=10)

        for article in articles[:5]:  # Get top 5 headlines
            text = article.get_text(strip=True)
            if text and len(text) > 10:  # Filter out very short text
                # Try to find the link associated with this headline
                link = None

                # Check if the heading itself contains a link
                a_tag = article.find('a')
                if a_tag and a_tag.get('href'):
                    link = a_tag.get('href')
                else:
                    # Check if the heading is inside a link
                    parent_a = article.find_parent('a')
                    if parent_a and parent_a.get('href'):
                        link = parent_a.get('href')
                    else:
                        # Look for the next link after this heading
                        next_a = article.find_next('a')
                        if next_a and next_a.get('href'):
                            link = next_a.get('href')

                # Make relative URLs absolute
                if link:
                    if link.startswith('/'):
                        link = f"https://www.deeplearning.ai{link}"
                    elif not link.startswith('http'):
                        link = f"https://www.deeplearning.ai/{link}"
                    headlines.append(f"• {text}\n  {link}")
                else:
                    headlines.append(f"• {text}")

        if headlines:
            return "Latest AI News from The Batch:\n\n" + "\n\n".join(headlines)
        else:
            return "Could not extract headlines. The page structure may have changed."

    except requests.exceptions.RequestException as e:
        return f"Error fetching newsletter: {str(e)}"
    except Exception as e:
        return f"Error parsing newsletter: {str(e)}"

def set_french_learning_goal(hours_per_week: float) -> str:
    """Set or update the weekly French learning goal in hours.

    Args:
        hours_per_week: Number of hours to study French per week

    Returns:
        Success message with the updated goal
    """
    try:
        stats_file = Path("stats.json")
        
        # Load existing stats or create new
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                stats = json.load(f)
        else:
            stats = {}
        
        # Update goal
        stats["weekly_goal_hours"] = hours_per_week
        stats["goal_updated_at"] = datetime.now().isoformat()
        
        # Save stats
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return f"✓ French learning goal set to {hours_per_week} hours per week"
    except Exception as e:
        return f"Error setting goal: {str(e)}"

def get_french_learning_goal() -> str:
    """Get the current weekly French learning goal.

    Returns:
        Current goal information or a message if no goal is set
    """
    try:
        stats_file = Path("stats.json")
        
        if not stats_file.exists():
            return "No French learning goal set yet. Set a goal to track your progress!"
        
        with open(stats_file, 'r') as f:
            stats = json.load(f)
        
        hours = stats.get("weekly_goal_hours")
        if hours is None:
            return "No French learning goal set yet. Set a goal to track your progress!"
        
        updated = stats.get("goal_updated_at", "Unknown")
        
        return f"Current goal: {hours} hours per week (Updated: {updated})"
    except Exception as e:
        return f"Error reading goal: {str(e)}"

def log_french_learning_time(hours: float, date: str = None) -> str:
    """Log actual French learning time for a study session.

    Args:
        hours: Number of hours studied in this session
        date: Date of the session (YYYY-MM-DD format). If not provided, uses today's date.

    Returns:
        Success message with the logged time
    """
    try:
        stats_file = Path("stats.json")
        
        # Load existing stats or create new
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                stats = json.load(f)
        else:
            stats = {}
        
        # Initialize learning_sessions list if it doesn't exist
        if "learning_sessions" not in stats:
            stats["learning_sessions"] = []
        
        # Use provided date or today's date
        session_date = date if date else datetime.now().strftime("%Y-%m-%d")
        
        # Add new session
        session = {
            "date": session_date,
            "hours": hours,
            "logged_at": datetime.now().isoformat()
        }
        stats["learning_sessions"].append(session)
        
        # Save stats
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return f"✓ Logged {hours} hours of French learning on {session_date}"
    except Exception as e:
        return f"Error logging learning time: {str(e)}"

def get_french_learning_time() -> str:
    """Get the actual French learning time for the current week.

    Returns:
        Summary of learning time for the current week
    """
    try:
        stats_file = Path("stats.json")
        
        if not stats_file.exists():
            return "No learning time logged yet. Start logging your study sessions!"
        
        with open(stats_file, 'r') as f:
            stats = json.load(f)
        
        sessions = stats.get("learning_sessions", [])
        
        if not sessions:
            return "No learning time logged yet. Start logging your study sessions!"
        
        # Get current week's Monday (ISO week)
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_start_str = week_start.strftime("%Y-%m-%d")
        
        # Filter sessions for current week
        current_week_sessions = []
        total_hours = 0
        
        for session in sessions:
            if session["date"] >= week_start_str:
                current_week_sessions.append(session)
                total_hours += session["hours"]
        
        if not current_week_sessions:
            return f"No learning time logged this week yet (week starting {week_start_str})"
        
        # Build detailed response
        response = f"This week's French learning time (week starting {week_start_str}):\n"
        response += f"Total: {total_hours} hours\n\n"
        response += "Sessions:\n"
        for session in current_week_sessions:
            response += f"  • {session['date']}: {session['hours']} hours\n"
        
        return response
    except Exception as e:
        return f"Error retrieving learning time: {str(e)}"

# Tool registry mapping tool names to functions
TOOL_FUNCTIONS: Dict[str, Callable] = {
    "write_to_file": write_to_file,
    "get_date": get_date,
    "get_batch_newsletter": get_batch_newsletter,
    "set_french_learning_goal": set_french_learning_goal,
    "get_french_learning_goal": get_french_learning_goal,
    "log_french_learning_time": log_french_learning_time,
    "get_french_learning_time": get_french_learning_time
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
    },
    {
        "type": "function",
        "function": {
            "name": "get_batch_newsletter",
            "description": "Get the latest AI news headlines from deeplearning.ai's The Batch newsletter",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_french_learning_goal",
            "description": "Set or update the weekly French learning goal in hours",
            "parameters": {
                "type": "object",
                "properties": {
                    "hours_per_week": {
                        "type": "number",
                        "description": "Number of hours to study French per week"
                    }
                },
                "required": ["hours_per_week"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_french_learning_goal",
            "description": "Get the current weekly French learning goal and see when it was last updated",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "log_french_learning_time",
            "description": "Log actual French learning time for a study session. Can optionally specify the date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "hours": {
                        "type": "number",
                        "description": "Number of hours studied in this session"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date of the session in YYYY-MM-DD format (optional, defaults to today)"
                    }
                },
                "required": ["hours"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_french_learning_time",
            "description": "Get the actual French learning time logged for the current week, including total hours and individual sessions",
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
