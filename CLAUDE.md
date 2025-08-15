# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gemme is a local file assistant powered by Gemma 3 270M that provides tool-calling capabilities for file operations. It's a Python-based CLI application that interfaces with Ollama to provide an AI assistant that can safely read, write, and manage text files within a sandboxed workspace.

## Development Commands

### Running the Application
```bash
python main.py                # Simple hello world entry point
uv run python rw_tools.py     # Interactive file assistant with Ollama integration
```

### Debugging Tool Calling Issues
- Type `debug` in the interactive mode to toggle verbose output
- Use verbose mode to see model responses and tool call detection
- Check that model parameters use low temperature (0.1) for reliable tool calling

### Dependencies Management
```bash
uv sync               # Install dependencies using uv
uv add <package>      # Add new dependencies
```

### Prerequisites
- Python 3.11+
- Ollama running locally (`ollama serve`)
- Gemma 3 270M model (`ollama pull gemma3:270m`)

## Architecture

### Core Components

**GemmaFileAssistant Class** (`rw_tools.py:14-395`): The main application class that:
- Manages secure file operations within a `./workspace` directory
- Provides 7 file operation tools: read_file, write_file, append_file, list_files, delete_file, file_info, search_in_files
- Handles communication with Ollama API for natural language processing
- Implements path sanitization for security (`_safe_path` method at line 43)

### Security Model
- All file operations are restricted to the `./workspace` directory
- Path traversal attacks are prevented through `_safe_path()` validation
- File content is truncated to 2000 characters for model context limits
- Search results are limited to 20 matches to prevent overwhelming the model

### Tool Calling Protocol
The assistant uses a specific format for tool calls:
```
TOOL: tool_name
ARGS: arguments
```

For write/append operations, use pipe-separated format: `filename|content`

### API Integration
- Communicates with Ollama at `http://localhost:11434`
- Uses temperature 0.7 for balanced creativity/consistency
- Implements timeout handling and error recovery
- Supports both single-shot and follow-up queries for tool results

## File Structure
- `main.py`: Simple entry point with hello world
- `rw_tools.py`: Complete file assistant implementation
- `workspace/`: Sandboxed directory for all file operations (created at runtime)
- `pyproject.toml`: Project configuration with minimal dependencies (requests)