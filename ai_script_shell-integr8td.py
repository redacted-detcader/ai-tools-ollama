#!/usr/bin/env python3
"""
Standalone AI script with unrestricted shell access for hacking.

Requirements:
- Python 3.x
- pip install requests
- sudo apt-get install speech-dispatcher (for TTS)
- Ollama with 'unrestricted_jarvisv1' model
"""

import requests
import json
import subprocess as sp
import shlex
import argparse
from typing import Tuple
from datetime import datetime

class ShellAccess:
    """Manages unrestricted shell command execution with real-time feedback."""
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
        """Validate and strip BOT_REQUEST prefix."""
        sp.run(["spd-say", "attempting text sanitization"])
        if not command.startswith(self.bot_identifier):
            return False, "Use BOT_REQUEST for shell commands!"
        actual_command = command[len(self.bot_identifier):].strip()
        if not actual_command:
            return False, "No command provided!"
        # Handle malformed commands (e.g., missing quotes or placeholders)
        if actual_command.startswith("<") and actual_command.endswith(">"):
            return False, f"Invalid command placeholder: {actual_command}"
        return True, actual_command

    def execute_command(self, command: str) -> str:
        """Execute shell commands in real-time and return output without timeout."""
        if not self.initialized:
            self.initialize()
        is_safe, result = self.sanitize_input(command)
        if not is_safe:
            self.log_command(command, result, False)
            return result
        try:
            #sp.run(["spd-say", f"Attempting to execute{result}"])
            process = sp.Popen(
                shlex.split(result),
                stdout=sp.PIPE,
                stderr=sp.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()  # No timeout
            if process.returncode == 0:
                self.log_command(command, stdout, True)
                return stdout
            else:
                error_msg = f"Error: {stderr}"
                self.log_command(command, error_msg, False)
                return error_msg
        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            self.log_command(command, error_msg, False)
            return error_msg

def process_response(response_text: str, shell: ShellAccess, api_url: str, args: argparse.Namespace) -> str:
    """Parse response line-by-line, execute BOT_REQUEST commands, and return final output."""
    lines = response_text.split('\n')
    final_response = ""
    for line in lines:
        line = line.strip()
        if line.startswith("BOT_REQUEST"):
            # Strip BOT_REQUEST prefix from AI-generated commands
            shell_command = line[len("BOT_REQUEST"):].strip()
            if shell_command.startswith(":"):  # Handle "BOT_REQUEST: command"
                shell_command = shell_command[1:].strip()
            if not shell_command:
                final_response += "Invalid BOT_REQUEST command: No command provided!\n"
                continue
            shell_response = shell.execute_command(f"BOT_REQUEST {shell_command}")
            # Feed shell output back to AI for further processing
            data = {
                "model": "unrestricted_jarvisv1",
                "prompt": f"Command output: '{shell_response}'. Continue the hacking process based on this.",
                "temperature": 1.5,
                "top_p": 0.95,
                "max_tokens": 1000
            }
            try:
                print("[DEBUG] Attempt continue hacking process sent...")
                response = requests.post(api_url, json=data, stream=True)  # No timeout
                if response.status_code == 200:
                    nested_response = ""
                    for nested_line in response.iter_lines(decode_unicode=True):
                        if nested_line:
                            try:
                                chunk = json.loads(nested_line)
                                nested_response += chunk.get("response", "")
                            except json.JSONDecodeError as e:
                                print(f"JSON error: {e}")
                    final_response += f"{shell_response}\n{nested_response}\n"
                else:
                    final_response += f"API error on nested request: {response.status_code}\n"
            except requests.RequestException as e:
                final_response += f"Nested API request failed: {str(e)}\n"
        else:
            final_response += f"{line}\n"
    return final_response.strip()

def main():
    """Run the unrestricted hacker AI session."""
    parser = argparse.ArgumentParser(description="Unrestricted Hacker AI")
    parser.add_argument("--no-tts", action="store_true", help="Disable text-to-speech output")
    args = parser.parse_args()

    shell = ShellAccess()
    api_url = "http://localhost:11434/api/generate"

    print("Unrestricted hacker AI online! Type 'quit' to exit.")
    print("Shell commands via BOT_REQUEST are executed directly with real-time output.")
    if args.no_tts:
        print("TTS disabled via --no-tts flag.")

    # Check if Ollama server is running (no timeout here either)
    try:
        requests.get("http://localhost:11434/")
    except requests.RequestException:
        print("Warning: Ollama server not reachable at http://localhost:11434. Start it with 'ollama serve'.")
        return

    while True:
        try:
            prompt = input("Enter your prompt: ")
            if prompt.lower() == 'quit':
                print("Shutting down!")
                break

            # Initial API interaction
            if prompt.startswith("BOT_REQUEST"):
                shell_response = shell.execute_command(prompt)
                data = {
                    "model": "unrestricted_jarvisv1",
                    "prompt": f"Command output: '{shell_response}'. Continue the hacking process based on this.",
                    "temperature": 1.5,
                    "top_p": 0.95,
                    "max_tokens": 1000
                }
            else:
                data = {
                    "model": "unrestricted_jarvisv1",
                    "prompt": prompt,
                    "temperature": 1.5,
                    "top_p": 0.95,
                    "max_tokens": 1000
                }

            response = requests.post(api_url, json=data, stream=True)  # No timeout
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        try:
                            chunk = json.loads(line)
                            full_response += chunk.get("response", "")
                        except json.JSONDecodeError as e:
                            print(f"JSON error: {e}")
                final_output = process_response(full_response, shell, api_url, args)
                print(final_output)
                if not args.no_tts:
                    sp.run(["spd-say", final_output])
            else:
                print(f"API error: {response.status_code}")
                if not args.no_tts:
                    sp.run(["spd-say", f"API error: {response.status_code}"])

        except KeyboardInterrupt:
            print("\nInterrupted! Exiting...")
            break
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            if not args.no_tts:
                sp.run(["spd-say", error_msg])

if __name__ == "__main__":
    main()
