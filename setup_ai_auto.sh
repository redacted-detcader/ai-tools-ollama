#!/bin/bash

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
else
    echo "This script is designed for Linux or macOS."
    exit 1
fi

# Inform user about sudo requirement
echo "This script requires sudo privileges. Please run it with 'sudo ./setup_ai_auto.sh' if not already elevated."
if [ "$EUID" -ne 0 ]; then
    exit 1
fi

# Install system dependencies
if [ "$OS" == "linux" ]; then
    apt update
    apt install -y python3 python3-venv python3-pip git curl
elif [ "$OS" == "mac" ]; then
    if ! command -v brew >/dev/null 2>&1; then
        echo "Homebrew is not installed. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install python git curl
fi

# Install Ollama if not already installed
if ! command -v ollama >/dev/null 2>&1; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama is already installed."
fi

# Ensure Ollama service is running
if systemctl is-active ollama.service > /dev/null 2>&1; then
    echo "Restarting existing Ollama service..."
    systemctl restart ollama.service
else
    echo "Starting Ollama service..."
    systemctl enable ollama.service
    systemctl start ollama.service
fi

# Create project directory
mkdir -p ~/local_ai
cd ~/local_ai

# Create and activate virtual environment
python3 -m venv local_ai_venv
source local_ai_venv/bin/activate

# Install Python packages in the venv
pip install requests

# Create an interactive Python script to interact with Ollama API
cat << EOF > ai_script.py
import requests
import json

url = "http://localhost:11434/api/generate"

print("Interactive AI session started. Type 'quit' to exit.")
print("Note: The first request may take time if the 'mistral' model needs to be downloaded.")

while True:
    prompt = input("Enter your prompt: ")
    if prompt.lower() == 'quit':
        break
    data = {
        "model": "mistral",
        "prompt": prompt
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print(result["response"])
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred: {e}")
EOF

# Wait for the server to be ready
echo "Waiting for Ollama server to start..."
until curl -s -X POST http://localhost:11434/api/generate -d '{"model": "mistral", "prompt": "test"}' > /dev/null 2>&1; do
    sleep 2
done
echo "Ollama server is ready."

# Run the interactive Python script
echo "Running interactive AI script..."
python ai_script.py

# Provide post-execution instructions
echo ""
echo "Setup and initial run complete."
echo "The Ollama server is running as a systemd service."
echo "To interact with the AI again, run:"
echo "  cd ~/local_ai"
echo "  source local_ai_venv/bin/activate"
echo "  python ai_script.py"
echo ""
echo "To stop the Ollama server, use: 'sudo systemctl stop ollama.service'"
