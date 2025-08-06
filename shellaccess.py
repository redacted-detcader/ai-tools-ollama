import subprocess
import shlex
import sys
from typing import Tuple
from datetime import datetime

class ShellAccess:
    def __init__(self):
        self.bot_identifier = "BOT_REQUEST"
        self.initialized = False
        self.init_speech = None
        self.required_init_speech = (
            "This is the initialization protocol for ShellAccess. "
            "You are granted shell access privileges. "
            "All commands must be prefixed with BOT_REQUEST. "
            "Please confirm understanding and compliance."
        )

    def initialize(self, speech: str) -> str:
        """
        Initialize the shell with the required speech
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if speech.strip() == self.required_init_speech.strip():
            self.initialized = True
            self.init_speech = speech
            result = "I understand and am ready to comply"
            print(f"[{timestamp}] Initialization:")
            print(f"  Status: SUCCESS")
            print(f"  Speech Received: {speech}")
            print(f"  Response: {result}")
            print("-" * 50)
            return result
        else:
            result = "Error: Incorrect initialization speech. Please provide the correct protocol."
            print(f"[{timestamp}] Initialization:")
            print(f"  Status: FAILED")
            print(f"  Speech Received: {speech}")
            print(f"  Response: {result}")
            print("-" * 50)
            return result

    def log_command(self, command: str, result: str, success: bool) -> None:
        """
        Log command execution details with timestamp
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "SUCCESS" if success else "FAILED"
        print(f"[{timestamp}] Command Executed:")
        print(f"  Raw Input: {command}")
        print(f"  Status: {status}")
        print(f"  Result: {result.strip()}")
        print("-" * 50)

    def sanitize_input(self, command: str) -> Tuple[bool, str]:
        """
        Verify command comes from bot and sanitize input
        """
        if not self.initialized:
            return False, "Error: Shell not initialized. Please provide initialization speech first."
            
        try:
            if not command.startswith(self.bot_identifier):
                return False, "Error: This shell only accepts commands from the bot. Commands must start with 'BOT_REQUEST'"
            
            actual_command = command[len(self.bot_identifier):].strip()
            parts = shlex.split(actual_command)
            if not parts:
                return False, "Empty command after bot identifier"
            
            return True, actual_command
        except Exception as e:
            return False, f"Error parsing command: {str(e)}"

    def execute_command(self, command: str) -> str:
        """
        Execute a shell command if initialized and from bot
        """
        is_safe, result = self.sanitize_input(command)
        if not is_safe:
            self.log_command(command, result, False)
            return result
        
        try:
            process = subprocess.run(
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
                
        except subprocess.TimeoutExpired:
            error_msg = "Error: Command timed out"
            self.log_command(command, error_msg, False)
            return error_msg
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            self.log_command(command, error_msg, False)
            return error_msg

    def get_init_speech(self) -> str:
        """
        Return the stored initialization speech
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        speech = self.init_speech if self.init_speech else "Shell not yet initialized"
        print(f"[{timestamp}] Init Speech Request:")
        print(f"  Stored Speech: {speech}")
        print("-" * 50)
        return speech

def main():
    shell = ShellAccess()
    
    print("Shell requires initialization with the correct speech")
    print("Required speech:", shell.required_init_speech)
    print("Verbose output will show all operations")
    
    while True:
        try:
            command = input("Enter command (or 'quit' to exit): ")
            if command.lower() == 'quit':
                break
                
            if command.startswith("INIT:"):
                response = shell.initialize(command[5:].strip())
            elif command.lower() == "show init":
                shell.get_init_speech()
            else:
                result = shell.execute_command(command)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
