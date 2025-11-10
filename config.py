"""Configuration management for the CLI chatbot."""
import os
from openai import OpenAI
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Project paths
PROJECT_DIR = Path(__file__).parent
MEMORY_FILE = PROJECT_DIR / "memory.json"
PROMPTS_FILE = PROJECT_DIR / "prompts.yaml"

# Load environment variables from .env file
load_dotenv(PROJECT_DIR / ".env")

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-5-nano"  

# Note: Memory management is now handled server-side by the Responses API
# Local memory.json is kept only for display/logging purposes

# Load prompts from YAML
def load_prompts():
    """Load prompts from YAML file."""
    with open(PROMPTS_FILE, 'r') as f:
        return yaml.safe_load(f)

# Logging configuration
LOG_LEVEL = "INFO"
