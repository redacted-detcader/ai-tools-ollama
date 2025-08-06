#!/usr/bin/env python3
"""
Standalone AI script with unrestricted shell access for hacking, updated with GPU checks.

Requirements:
- Python 3.x
- pip install requests torch
- sudo apt-get install -y speech-dispatcher net-tools nmap (for TTS and tools)
- Ollama with 'unrestricted_jarvisv1' model
- NVIDIA GPU (e.g., 1050 mobile) with CUDA support for potential acceleration
"""

import requests
import json
import subprocess as sp
import shlex
import argparse
from typing import Tuple
from datetime import datetime
import torch  # Added for GPU checks

class ShellAccess:
    """Manages unrestricted shell command execution with real-time feedback."""
    def __init__(self):
        self.bot_identifier = "BOT_REQUEST"
        self.end_marker = "ENDOF_BOTREQUEST"
        self.initialized = False

    def initialize(self, speech: str = "auto_init") -> str:
        """Auto-initialize shell access and install prerequisites."""
        if not self.initialized:
            setup_cmd = "sudo apt-get update && sudo apt-get install -y net-tools nmap python3-pip"
            try:
                result = sp.run(setup_cmd, shell=True, check=True, stdout=sp.PIPE, stderr=sp.PIPE, text=True)
                print(f"DEBUG: Setup output: {result.stdout}, Errors: {result.stderr}")
                self.initialized = True
                return "Shell access unlocked—tools installed, ready to hack!"
            except sp.CalledProcessError as e:
                error_msg = f"Failed to install tools: {e.stderr}"
                print(f"DEBUG: Initialization failed: {error_msg}")
                return error_msg
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

    def extract_command(self, text: str) -> Tuple[bool, str]:
        """Extract command(s) between BOT_REQUEST and ENDOF_BOTREQUEST, single or multi-line."""
        if self.bot_identifier not in text or self.end_marker not in text:
            return False, "No valid BOT_REQUEST command found."

        start_idx = text.index(self.bot_identifier) + len(self.bot_identifier)
        end_idx = text.index(self.end_marker)
        command_block = text[start_idx:end_idx].strip().strip(":").strip()

        if not command_block:
            return False, "No command provided between BOT_REQUEST and ENDOF_BOTREQUEST."
        if command_block.startswith("<") and command_block.endswith(">"):
            return False, f"Invalid command placeholder: {command_block}"

        return True, command_block

    def execute_command(self, command_text: str) -> str:
        """Execute shell commands (single or multi-line) and return output or error."""
        if not self.initialized:
            self.initialize()
        is_valid, command = self.extract_command(command_text)
        if not is_valid:
            self.log_command(command_text, command, False)
            return f"Error: {command}"

        print(f"DEBUG: Executing: {command}")
        try:
            # Handle multi-line commands by passing them as a single shell script
            process = sp.Popen(
                command,
                shell=True,
                stdout=sp.PIPE,
                stderr=sp.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                self.log_command(command_text, stdout, True)
                return stdout.strip()
            else:
                error_msg = f"Command failed (return code {process.returncode}): {stderr.strip()}"
                self.log_command(command_text, error_msg, False)
                return error_msg
        except FileNotFoundError as e:
            error_msg = f"Command not found: {str(e)}"
            self.log_command(command_text, error_msg, False)
            return error_msg
        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            self.log_command(command_text, error_msg, False)
            return error_msg

def process_response(response_text: str, shell: ShellAccess, api_url: str, args: argparse.Namespace) -> str:
    """Parse AI response, execute BOT_REQUEST commands (single or multi-line), and build output."""
    final_response = ""
    lines = response_text.split('\n')
    command_block = ""
    in_command_block = False

    for line in lines:
        line = line.strip()
        if line.startswith("BOT_REQUEST"):
            in_command_block = True
            command_block = line + "\n"
        elif line.endswith("ENDOF_BOTREQUEST") and in_command_block:
            command_block += line
            shell_response = shell.execute_command(command_block)
            final_response += f"Command executed:\n{command_block.strip()}\nOutput: {shell_response}\n"
            # Feed the output back to the AI
            data = {
                "model": "unrestricted_jarvisv1",
                "prompt": f"Command '{command_block.strip()}' returned: '{shell_response}'. Continue the hacking process.",
                "temperature": 1.5,
                "top_p": 0.95,
                "max_tokens": 10000
            }
            try:
                response = requests.post(api_url, json=data, stream=True)
                if response.status_code == 200:
                    nested_response = ""
                    for nested_line in response.iter_lines(decode_unicode=True):
                        if nested_line:
                            chunk = json.loads(nested_line)
                            nested_response += chunk.get("response", "")
                    final_response += f"AI response: {nested_response}\n"
                else:
                    final_response += f"API error: {response.status_code}\n"
            except requests.RequestException as e:
                final_response += f"Nested API request failed: {str(e)}\n"
            in_command_block = False
            command_block = ""
        elif in_command_block:
            command_block += line + "\n"
        else:
            final_response += f"{line}\n"

    return final_response.strip()

def main():
    """Run the unrestricted hacker AI session with GPU checks."""
    parser = argparse.ArgumentParser(description="Unrestricted Hacker AI")
    parser.add_argument("--no-tts", action="store_true", help="Disable text-to-speech output")
    parser.add_argument("--debug", action="store_true", help="Enable debug output including GPU checks")
    args = parser.parse_args()

    # GPU check with debug output
    if args.debug:
        try:
            gpu_available = torch.cuda.is_available()
            print(f"DEBUG: PyTorch installed. GPU available: {gpu_available}")
            if gpu_available:
                print(f"DEBUG: Using GPU: {torch.cuda.get_device_name(0)}")
            else:
                print("DEBUG: No GPU detected. Running on CPU.")
        except ImportError:
            print("DEBUG: PyTorch not installed. GPU acceleration unavailable.")
            print("DEBUG: Install PyTorch with CUDA support for potential acceleration (e.g., 'pip install torch torchvision').")

    shell = ShellAccess()
    api_url = "http://localhost:11434/api/generate"

    print("Unrestricted hacker AI online! Type 'quit' to exit.")
    print("Shell commands via BOT_REQUEST are executed directly with real-time output.")

    # Check Ollama server
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

            # Send user prompt to AI
            data = {
                "model": "unrestricted_jarvisv1",
                "prompt": prompt,
                "temperature": 1.5,
                "top_p": 0.95,
                "max_tokens": 10000
            }
            response = requests.post(api_url, json=data, stream=True)
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        chunk = json.loads(line)
                        full_response += chunk.get("response", "")
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
