# Gemme Tool Use Quick Start Guide

Get up and running with the Gemma 3 270M local file assistant in minutes.

## Prerequisites

- macOS (for brew install) or Linux
- Python 3.11+
- Terminal access

## Installation Steps

### 1. Install Ollama
```bash
brew install ollama
```

### 2. Start Ollama Service
```bash
ollama serve
```
*Keep this terminal open - Ollama needs to run in the background*

### 3. Pull the Gemma 3 270M Model
Open a new terminal and run:
```bash
ollama pull gemma3:270m
```

### 4. Set Up Python Environment
```bash
uv sync
```

### 5. Start the File Assistant
```bash
uv run python rw_tools.py
```

## First Steps

Once the assistant starts, try these commands:

1. **Create a file:**
   ```
   Create a shopping list for spaghetti dinner
   ```

2. **List files:**
   ```
   Show me all my files
   ```

3. **Read a file:**
   ```
   Read my shopping list
   ```

4. **Add to a file:**
   ```
   Add garlic bread to my shopping list
   ```

## Debug Mode

Debug mode is enabled by default to help you see what's happening. You'll see:
- `[DEBUG] Sending prompt to model...`
- `[DEBUG] Model response: TOOL: write_file...`
- `[DEBUG] Tool call detected in response`

Type `debug` to toggle verbose output on/off.

## Workspace

All files are created in the `./workspace` directory for security. The assistant cannot access files outside this sandbox.

## Troubleshooting

**"Error communicating with Ollama"**
- Make sure `ollama serve` is running in another terminal
- Check that the gemma3:270m model was downloaded successfully

**Assistant not using tools**
- Debug mode will show if tool calls are detected
- The model should respond with `TOOL: toolname` format
- Check that your request clearly asks for file operations

## Exit

Type `quit`, `exit`, or `q` to stop the assistant.
