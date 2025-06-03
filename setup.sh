#!/bin/bash

# Create project directory structure
mkdir -p mcp-dual-chatbot/templates
cd mcp-dual-chatbot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install flask==2.3.3 openai==0.28.1 mcp==0.4.0

# Set OpenAI API key 
export OPENAI_API_KEY="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"

echo "Setup complete! Now run the application with:"
echo "python app.py"