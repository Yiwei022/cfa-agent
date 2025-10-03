"""Configuration management for the CLI chatbot."""
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Project paths
PROJECT_DIR = Path(__file__).parent
MEMORY_FILE = PROJECT_DIR / "memory.json"
PROMPTS_FILE = PROJECT_DIR / "prompts.yaml"

# Load environment variables from .env file
load_dotenv(PROJECT_DIR / ".env")

# Mistral API configuration
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_MODEL = "mistral-large-latest"  # Supports function calling

# Memory management
MEMORY_THRESHOLD_KB = 50  # Threshold to trigger summarization
MEMORY_KEEP_LAST_N = 10   # Keep last N messages after summarization

# Load prompts from YAML
def load_prompts():
    """Load prompts from YAML file."""
    with open(PROMPTS_FILE, 'r') as f:
        return yaml.safe_load(f)

# Logging configuration
LOG_LEVEL = "INFO"
