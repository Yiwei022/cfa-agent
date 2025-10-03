"""Unit tests for memory management."""
import pytest
import json
from pathlib import Path
from memory import (
    load_memory, save_memory, get_memory_size_kb,
    should_summarize, create_summary_request,
    compress_memory, add_message
)


@pytest.fixture
def temp_memory_file(tmp_path, monkeypatch):
    """Create a temporary memory file for testing."""
    temp_file = tmp_path / "test_memory.json"

    # Patch MEMORY_FILE in the memory module
    import memory
    monkeypatch.setattr(memory, 'MEMORY_FILE', temp_file)

    yield temp_file

    # Cleanup
    if temp_file.exists():
        temp_file.unlink()


def test_load_memory_empty(temp_memory_file):
    """Test loading memory when file doesn't exist."""
    messages = load_memory()
    assert messages == []


def test_save_and_load_memory(temp_memory_file):
    """Test saving and loading memory."""
    test_messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]

    save_memory(test_messages)
    loaded = load_memory()

    assert loaded == test_messages


def test_get_memory_size_kb():
    """Test calculating memory size."""
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"}
    ]

    size = get_memory_size_kb(messages)
    assert size > 0
    assert isinstance(size, float)


def test_should_summarize():
    """Test summarization threshold check."""
    # Small messages should not trigger summarization
    small_messages = [{"role": "user", "content": "Hi"}]
    assert not should_summarize(small_messages)

    # Large messages should trigger summarization
    large_content = "x" * 60000  # 60KB of content
    large_messages = [{"role": "user", "content": large_content}]
    assert should_summarize(large_messages)


def test_add_message():
    """Test adding messages to history."""
    messages = []

    messages = add_message(messages, "user", "Hello")
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"

    messages = add_message(messages, "assistant", "Hi there!")
    assert len(messages) == 2


def test_create_summary_request():
    """Test creating summarization request."""
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"},
        {"role": "user", "content": "How are you?"}
    ]

    prompt_template = "Summarize: {conversation}"
    summary_request = create_summary_request(messages, prompt_template)

    assert "USER: Hello" in summary_request
    assert "ASSISTANT: Hi!" in summary_request
    assert "USER: How are you?" in summary_request


def test_compress_memory():
    """Test memory compression."""
    messages = [
        {"role": "user", "content": f"Message {i}"}
        for i in range(20)
    ]

    summary = "This is a summary of the conversation"
    compressed = compress_memory(messages, summary)

    # Should have summary + last 10 messages (MEMORY_KEEP_LAST_N)
    assert len(compressed) == 11
    assert compressed[0]["role"] == "system"
    assert summary in compressed[0]["content"]

    # Check that last messages are preserved
    assert compressed[-1]["content"] == "Message 19"


def test_load_memory_invalid_json(temp_memory_file):
    """Test loading memory with invalid JSON."""
    # Write invalid JSON
    temp_memory_file.write_text("invalid json content")

    messages = load_memory()
    assert messages == []
