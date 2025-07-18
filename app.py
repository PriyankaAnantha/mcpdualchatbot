#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
import openai
import subprocess
import json
import os
from pathlib import Path
import tempfile

app = Flask(__name__)

# Configure OpenAI 
openai.api_key = os.getenv('OPENAI_API_KEY', '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')

# MCP client functions
def call_mcp_tool(tool_name, arguments=None):
    """Call MCP server tool via subprocess."""
    try:
        cmd_input = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        }
        
        result = subprocess.run(
            ['python', 'server.py'],
            input=json.dumps(cmd_input),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            return response.get('result', {}).get('content', [{}])[0].get('text', '')
        return f"Error: {result.stderr}"
    except Exception as e:
        return f"Error calling MCP: {str(e)}"

def get_llm_response(prompt, model="gpt-3.5-turbo"):
    """Get response from selected LLM."""
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_document', methods=['POST'])
def upload_document():
    """Upload document via MCP server."""
    try:
        file = request.files['file']
        if file and file.filename:
            content = file.read().decode('utf-8')
            result = call_mcp_tool('upload_document', {
                'name': file.filename,
                'content': content
            })
            return jsonify({'success': True, 'message': result})
        return jsonify({'success': False, 'message': 'No file provided'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/chat', methods=['POST'])
def chat():
    """Handle dual chat requests."""
    data = request.json
    query = data.get('query', '')
    model = data.get('model', 'gpt-3.5-turbo')
    
    # Base LLM response (left side)
    base_response = get_llm_response(query, model)
    
    # RAG-enhanced response (right side)
    rag_context = call_mcp_tool('get_rag_context', {'query': query})
    enhanced_prompt = f"Context: {rag_context}\n\nQuestion: {query}"
    rag_response = get_llm_response(enhanced_prompt, model)
    
    return jsonify({
        'base_response': base_response,
        'rag_response': rag_response,
        'context_used': rag_context
    })

@app.route('/save_conversation', methods=['POST'])
def save_conversation():
    """Save conversation history."""
    conversation = request.json.get('conversation', [])
    result = call_mcp_tool('save_conversation', {'conversation': conversation})
    return jsonify({'success': True, 'message': result})

@app.route('/list_documents', methods=['GET'])
def list_documents():
    """List uploaded documents."""
    result = call_mcp_tool('list_documents')
    return jsonify({'documents': result})

if __name__ == '__main__':
    app.run(debug=True, port=5000)