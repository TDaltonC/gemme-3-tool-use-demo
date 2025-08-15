#!/usr/bin/env python3
"""
Gemma 3 270M Local File Assistant
A simple tool-calling agent that can read and write text files locally.
"""

import json
import requests
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

class GemmaFileAssistant:
    """A file management assistant powered by Gemma 3 270M."""
    
    def __init__(self, model: str = "gemma3:270m", workspace: str = "./workspace"):
        """
        Initialize the file assistant.
        
        Args:
            model: The Ollama model to use
            workspace: Directory for file operations (for safety)
        """
        self.model = model
        self.base_url = "http://localhost:11434"
        self.workspace = Path(workspace)
        
        # Create workspace if it doesn't exist
        self.workspace.mkdir(exist_ok=True)
        
        # Define available tools
        self.tools = {
            "read_file": self.read_file,
            "write_file": self.write_file,
            "append_file": self.append_file,
            "list_files": self.list_files,
            "delete_file": self.delete_file,
            "file_info": self.file_info,
            "search_in_files": self.search_in_files
        }
    
    def _safe_path(self, filename: str) -> Optional[Path]:
        """
        Ensure the path is within the workspace directory.
        
        Args:
            filename: The filename to validate
            
        Returns:
            Safe path or None if invalid
        """
        try:
            # Resolve the path and ensure it's within workspace
            file_path = (self.workspace / filename).resolve()
            if self.workspace.resolve() not in file_path.parents and file_path != self.workspace.resolve():
                if not file_path.is_relative_to(self.workspace.resolve()):
                    return None
            return file_path
        except Exception:
            return None
    
    def read_file(self, filename: str) -> str:
        """Read the contents of a text file.
        
        Args:
            filename: Name of the file to read (e.g., 'notes.txt', 'data/info.txt')
        """
        file_path = self._safe_path(filename)
        if not file_path:
            return f"Error: Invalid file path '{filename}'"
        
        try:
            if not file_path.exists():
                return f"Error: File '{filename}' does not exist"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Limit size for model context
                if len(content) > 2000:
                    return f"File content (truncated to 2000 chars):\n{content[:2000]}..."
                return f"File content:\n{content}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def write_file(self, args: str) -> str:
        """Create or overwrite a text file with content.
        
        Args:
            args: Must be in format 'filename|content' where:
                - filename: Name of file to create (e.g., 'shopping.txt', 'notes/todo.txt')
                - content: Text content to write to the file
        
        Example: 'shopping.txt|Eggs\nMilk\nBread'
        """
        try:
            parts = args.split('|', 1)
            if len(parts) != 2:
                return "Error: Use format 'filename|content'"
            
            filename, content = parts
            file_path = self._safe_path(filename.strip())
            
            if not file_path:
                return f"Error: Invalid file path '{filename}'"
            
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Successfully wrote {len(content)} characters to '{filename}'"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    def append_file(self, args: str) -> str:
        """Add content to the end of an existing text file.
        
        Args:
            args: Must be in format 'filename|content' where:
                - filename: Name of existing file to append to (e.g., 'log.txt', 'notes.txt')
                - content: Text content to add to the end of the file
        
        Example: 'log.txt|New entry: Task completed'
        """
        try:
            parts = args.split('|', 1)
            if len(parts) != 2:
                return "Error: Use format 'filename|content'"
            
            filename, content = parts
            file_path = self._safe_path(filename.strip())
            
            if not file_path:
                return f"Error: Invalid file path '{filename}'"
            
            # Create file if it doesn't exist
            if not file_path.exists():
                return self.write_file(args)
            
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)
            
            return f"Successfully appended {len(content)} characters to '{filename}'"
        except Exception as e:
            return f"Error appending to file: {str(e)}"
    
    def list_files(self, pattern: str = "*") -> str:
        """List files in the workspace directory.
        
        Args:
            pattern: File pattern to match (default: '*' for all files)
                - '*' shows all files
                - '*.txt' shows only .txt files  
                - '*.py' shows only Python files
                - 'data/*' shows files in data folder
        
        Example: '*' or '*.txt' or 'notes/*'
        """
        try:
            files = []
            
            # Use glob pattern matching
            for file_path in self.workspace.glob(pattern):
                if file_path.is_file():
                    rel_path = file_path.relative_to(self.workspace)
                    size = file_path.stat().st_size
                    files.append(f"- {rel_path} ({size} bytes)")
            
            if not files:
                return f"No files found matching pattern '{pattern}'"
            
            return f"Files in workspace:\n" + "\n".join(files)
        except Exception as e:
            return f"Error listing files: {str(e)}"
    
    def delete_file(self, filename: str) -> str:
        """Permanently delete a file from the workspace.
        
        Args:
            filename: Name of the file to delete (e.g., 'old_notes.txt', 'temp/data.txt')
        """
        file_path = self._safe_path(filename)
        if not file_path:
            return f"Error: Invalid file path '{filename}'"
        
        try:
            if not file_path.exists():
                return f"Error: File '{filename}' does not exist"
            
            file_path.unlink()
            return f"Successfully deleted '{filename}'"
        except Exception as e:
            return f"Error deleting file: {str(e)}"
    
    def file_info(self, filename: str) -> str:
        """Get detailed information about a file (size, dates, line count).
        
        Args:
            filename: Name of the file to inspect (e.g., 'document.txt', 'data/log.txt')
        """
        file_path = self._safe_path(filename)
        if not file_path:
            return f"Error: Invalid file path '{filename}'"
        
        try:
            if not file_path.exists():
                return f"Error: File '{filename}' does not exist"
            
            stat = file_path.stat()
            info = [
                f"File: {filename}",
                f"Size: {stat.st_size} bytes",
                f"Modified: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}",
                f"Created: {datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}"
            ]
            
            # Add line count for text files
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = sum(1 for _ in f)
                info.append(f"Lines: {lines}")
            except:
                pass
            
            return "\n".join(info)
        except Exception as e:
            return f"Error getting file info: {str(e)}"
    
    def search_in_files(self, search_term: str) -> str:
        """Search for text within all .txt files in the workspace.
        
        Args:
            search_term: Text to search for (case-insensitive, e.g., 'shopping', 'TODO', 'important')
        """
        try:
            results = []
            
            for file_path in self.workspace.glob("**/*.txt"):
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            for i, line in enumerate(lines, 1):
                                if search_term.lower() in line.lower():
                                    rel_path = file_path.relative_to(self.workspace)
                                    results.append(f"{rel_path}:{i}: {line.strip()[:80]}")
                    except:
                        continue
            
            if not results:
                return f"No matches found for '{search_term}'"
            
            # Limit results
            if len(results) > 20:
                results = results[:20]
                results.append(f"... and {len(results) - 20} more matches")
            
            return f"Search results for '{search_term}':\n" + "\n".join(results)
        except Exception as e:
            return f"Error searching files: {str(e)}"
    
    def query(self, prompt: str, verbose: bool = False) -> str:
        """
        Process a user query, potentially using tools.
        
        Args:
            prompt: The user's question or request
            verbose: Whether to print debug information
            
        Returns:
            The assistant's response
        """
        # Create tool descriptions
        tool_descriptions = []
        for name, func in self.tools.items():
            doc = func.__doc__ or "No description"
            tool_descriptions.append(f"- {name}: {doc}")
        
        tools_text = "\n".join(tool_descriptions)
        
        # Build the full prompt with stronger tool-calling guidance
        system_prompt = f"""You are a file assistant. When users ask you to work with files, you MUST use tools.

WORKSPACE: {self.workspace.absolute()}

AVAILABLE TOOLS:
{tools_text}

CRITICAL: When a user asks you to create, write, read, list, delete, or search files, you MUST respond with this EXACT format:

TOOL: tool_name
ARGS: arguments

EXAMPLES:
User: "Create a shopping list file"
Response:
TOOL: write_file
ARGS: shopping_list.txt|Shopping List:
- Spaghetti noodles
- Tomato sauce
- Ground beef
- Parmesan cheese
- Garlic bread

User: "Make a file called notes.txt with my thoughts"
Response:
TOOL: write_file
ARGS: notes.txt|Today's thoughts:
This is my first note.
I need to remember to call mom.

User: "Read the shopping list"
Response:
TOOL: read_file
ARGS: shopping_list.txt

User: "Add milk to my shopping list"
Response:
TOOL: append_file
ARGS: shopping_list.txt|
- Milk

User: "Show me all my files"
Response:
TOOL: list_files
ARGS: *

CRITICAL FORMAT RULES:
- write_file and append_file MUST use: filename|content
- The pipe | separates filename from content
- Everything after | is the file content
- Use actual filenames like 'shopping.txt', 'notes.txt', 'list.txt'

User request: {prompt}"""
        
        if verbose:
            print(f"[DEBUG] Sending prompt to model...")
        
        # Query the model
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_k": 10,
                        "top_p": 0.8,
                        "num_predict": 512
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()['response']
        except requests.exceptions.RequestException as e:
            return f"Error communicating with Ollama: {str(e)}. Is Ollama running?"
        
        if verbose:
            print(f"[DEBUG] Model response: {result[:200]}...")
        
        # Check if the model wants to use a tool
        if "TOOL:" in result:
            if verbose:
                print(f"[DEBUG] Tool call detected in response")
            lines = result.split('\n')
            tool_name = None
            args = ""
            
            for i, line in enumerate(lines):
                if line.strip().startswith("TOOL:"):
                    tool_name = line.replace("TOOL:", "").strip()
                elif line.strip().startswith("ARGS:"):
                    # Get everything after ARGS:
                    args = line.replace("ARGS:", "").strip()
                    # Also check if args continue on next lines
                    if i + 1 < len(lines) and not lines[i + 1].strip().startswith("TOOL:"):
                        # Might be multi-line content
                        remaining = "\n".join(lines[i + 1:])
                        if remaining.strip():
                            args = args + "\n" + remaining
                            break
            
            if verbose:
                print(f"[DEBUG] Tool: {tool_name}, Args: {args[:100]}...")
            
            if tool_name and tool_name in self.tools:
                # Execute the tool
                if args:
                    tool_result = self.tools[tool_name](args)
                else:
                    tool_result = self.tools[tool_name]("")
                
                if verbose:
                    print(f"[DEBUG] Tool result: {tool_result[:200]}...")
                
                # Get final response from model
                followup = f"""The tool '{tool_name}' returned: {tool_result}

Based on this result, please provide a helpful response to the user's original request: {prompt}"""
                
                try:
                    response = requests.post(
                        f"{self.base_url}/api/generate",
                        json={
                            "model": self.model,
                            "prompt": followup,
                            "stream": False,
                            "options": {
                                "temperature": 0.3,
                                "num_predict": 256
                            }
                        },
                        timeout=30
                    )
                    response.raise_for_status()
                    return response.json()['response']
                except:
                    # If follow-up fails, return tool result
                    return tool_result
            else:
                if tool_name:
                    return f"Unknown tool: {tool_name}. Available tools: {', '.join(self.tools.keys())}"
        
        return result


def main():
    """Interactive demo of the file assistant."""
    print("=" * 60)
    print("Gemma 3 270M File Assistant")
    print("=" * 60)
    print("\nInitializing... Make sure Ollama is running!")
    print("(Run 'ollama serve' in another terminal if needed)\n")
    
    # Create assistant
    assistant = GemmaFileAssistant()
    print(f"Workspace: {assistant.workspace.absolute()}")
    print("\nExample commands:")
    print("- 'List all files'")
    print("- 'Create a file called todo.txt with my tasks'")
    print("- 'Read todo.txt'")
    print("- 'Add a new line to todo.txt'")
    print("- 'Search for keyword in all files'")
    print("\nType 'quit' to exit, 'debug' to toggle verbose mode\n")
    
    verbose = True
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'debug':
                verbose = not verbose
                print(f"Debug mode: {'ON' if verbose else 'OFF'}")
                continue
            
            if not user_input:
                continue
            
            print("\nAssistant: ", end="", flush=True)
            response = assistant.query(user_input, verbose=verbose)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")


if __name__ == "__main__":
    main()