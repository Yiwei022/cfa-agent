# Installation Guide for Lalaby

## Quick Install

The easiest way to install Lalaby is using pip in editable mode:

```bash
# Clone the repository
git clone https://github.com/bcivitcioglu/cfa-agent.git
cd cfa-agent

# Install the package
pip install -e .
```

## Setup API Key

Create a `.env` file in the project directory:

```bash
cd /Users/davy/repo/cfa-agent
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

**Important:** Keep your `.env` file in the project directory where `prompts.yaml` and other config files are located.

## Running Lalaby

### Option 1: Using the Command (if in PATH)

If your Python bin directory is in your PATH:

```bash
lalaby
```

### Option 2: Using Python directly

If the command isn't found, you can run it with:

```bash
python3 -c "from main import main; main()"
```

Or from the project directory:

```bash
python3 main.py
```

### Option 3: Add Python bin to PATH

To use the `lalaby` command from anywhere, add Python's bin directory to your PATH:

**For macOS/Linux** (add to `~/.zshrc` or `~/.bashrc`):

```bash
# For system Python
export PATH="/Library/Frameworks/Python.framework/Versions/3.13/bin:$PATH"

# Or for user Python
export PATH="$HOME/Library/Python/3.x/bin:$PATH"

# Or find your Python bin directory with:
python3 -c "import sys; print(sys.exec_prefix + '/bin')"
```

Then reload your shell:

```bash
source ~/.zshrc  # or source ~/.bashrc
```

## Verifying Installation

Check that the package is installed:

```bash
pip show lalaby
```

You should see:

```
Name: lalaby
Version: 1.0.0
Summary: An AI-powered French learning assistant with goal tracking and progress monitoring
```

## Uninstalling

To uninstall:

```bash
pip uninstall lalaby
```

## Troubleshooting

### "lalaby: command not found"

This means the Python bin directory isn't in your PATH. Use Option 2 or Option 3 above.

### "OPENAI_API_KEY environment variable not set"

Make sure you created the `.env` file in the project directory (`/Users/davy/repo/cfa-agent/.env`).

### Import errors

Make sure you installed the dependencies:

```bash
pip install -e .
```

This will install all required packages: `openai`, `rich`, `python-dotenv`, `PyYAML`, `pypdf`.

## Development Installation

For development with testing tools:

```bash
pip install -e ".[dev]"
```

This installs additional packages: `pytest`, `pytest-cov`.

## Running Tests

```bash
cd /Users/davy/repo/cfa-agent
python -m pytest tests/ -v
```

