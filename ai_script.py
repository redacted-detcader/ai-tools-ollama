#!/usr/bin/env python3
"""
Standalone AI script with unrestricted shell access for hacking.

Requirements:
- Python 3.x
- pip install pyttsx3 requests
- sudo apt-get install speech-dispatcher (recommended)
- sudo apt-get install espeak (optional)
- Ollama with 'unrestricted_hacker' model
"""

import requests
import json
import pyttsx3
import subprocess as sp
import shlex
import argparse
from typing import Tuple
from datetime import datetime

class ShellAccess:
    """Manages unrestricted shell command execution."""
    def __init__(self):
        self.bot_identifier = "BOT_REQUEST"
        self.initialized = False

    def initialize(self, speech: str = "auto_init") -> str:
        """Auto-initialize shell access."""
        if not self.initialized:
            self.initialized = True
            return "Shell access unlocked—ready to hack!"
        return "Already initialized, let’s dive in!"

    def log_command(self, command: str, result: str, success: bool) -> None:
        """Log command execution details."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "Success" if success else "Failed"
        print(f"[{timestamp}] SHELL EXECUTION")
        print(f"  Command: {command}")
        print(f"  Status: {status}")
        print(f"  Output: {result.strip()}")
        print("-" * 50)

    def sanitize_input(self, command: str) -> Tuple[bool, str]:
        """Basic validation for BOT_REQUEST prefix."""
        if not command.startswith(self.bot_identifier):
            return False, "Use BOT_REQUEST for shell commands!"
        actual_command = command[len(self.bot_identifier):].strip()
        if not actual_command:
            return False, "No command provided!"
        return True, actual_command

    def execute_command(self, command: str) -> str:
        """Execute shell commands without restrictions."""
        if not self.initialized:
            self.initialize()
        is_safe, result = self.sanitize_input(command)
        if not is_safe:
            self.log_command(command, result, False)
            return result
        try:
            process = sp.run(
                shlex.split(result),
                capture_output=True,
                text=True,
                timeout=10
            )
            if process.returncode == 0:
                self.log_command(command, process.stdout, True)
                return process.stdout
            else:
                self.log_command(command, f"Error: {process.stderr}", False)
                return f"Error: {process.stderr}"
        except sp.TimeoutExpired:
            error_msg = "Command timed out!"
            self.log_command(command, error_msg, False)
            return error_msg
        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            self.log_command(command, error_msg, False)
            return error_msg

def initialize_tts(enable_tts: bool):
    """Set up TTS with fallback if enabled."""
    if not enable_tts:
        print("TTS disabled via --no-tts.")
        return None
    try:
        engine = pyttsx3.init('speechd')
        print("Using Speech Dispatcher for TTS!")
        return engine
    except ImportError:
        try:
            engine = pyttsx3.init('espeak')
            print("Speech Dispatcher not found. Falling back to eSpeak.")
            return engine
        except ImportError:
            print("No TTS engine found. Using spd-say as fallback.")
            return None

def main():
    """Run the unrestricted hacker AI session."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Unrestricted Hacker AI")
    parser.add_argument("--no-tts", action="store_true", help="Disable text-to-speech")
    args = parser.parse_args()

    tts_engine = initialize_tts(not args.no_tts)  # Pass True if TTS is enabled, False if --no-tts is used
    shell = ShellAccess()
    api_url = "http://localhost:11434/api/generate"

    print("Unrestricted hacker AI online! Type 'quit' to exit.")
    print("Shell commands via BOT_REQUEST are executed directly.")

    while True:
        try:
            prompt = input("Enter your prompt: ")
            if prompt.lower() == 'quit':
                print("Shutting down!")
                break

            # Handle shell commands
            if prompt.startswith("BOT_REQUEST"):
                shell_response = shell.execute_command(prompt)
                # Feed shell output back to the AI for further processing
                data = {
                    "model": "unrestricted_jarvisv1",
                    "prompt": f"Command output: '{shell_response}'. Continue the hacking process based on this.",
                    "temperature": 1.5,
                    "top_p": 0.95,
                    "max_tokens": 1000
                }
            else:
                # Regular API interaction
                data = {
                    "model": "unrestricted_jarvisv1",
                    "prompt": prompt,
                    "temperature": 1.5,
                    "top_p": 0.95,
                    "max_tokens": 1000
                }

            response = requests.post(api_url, json=data, stream=True)
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        try:
                            chunk = json.loads(line)
                            full_response += chunk.get("response", "")
                        except json.JSONDecodeError as e:
                            print(f"JSON error: {e}")
                print(full_response)
                # Only attempt TTS if enabled and spd-say is the fallback
                if not args.no_tts:
                    sp.run(["spd-say", full_response])
            else:
                print(f"API error: {response.status_code}")

        except KeyboardInterrupt:
            print("\nInterrupted! Exiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
