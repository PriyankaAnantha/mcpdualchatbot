#!/bin/bash

# Create project directory structure
mkdir -p mcp-dual-chatbot/templates
cd mcp-dual-chatbot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install flask==2.3.3 requests==2.31.0 mcp==0.4.0

echo "Setup complete!"
echo ""
echo "IMPORTANT: Before running the app, make sure Ollama is installed and running:"
echo "1. Install Ollama from: https://ollama.ai"
echo "2. Start Ollama: ollama serve"
echo "3. Pull a model: ollama pull llama2"
echo ""
echo "Then run the application with:"
echo "python app.py"