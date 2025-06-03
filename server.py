#!/usr/bin/env python3
import asyncio
import json
from typing import Any, Sequence
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
import tempfile
import os
from pathlib import Path

# Simple in-memory storage
documents = {}
conversations = []

server = Server("dual-chatbot-platform")

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available document resources."""
    return [
        Resource(
            uri=f"document://{doc_id}",
            name=f"Document: {info['name']}",
            description=f"Uploaded document: {info['name']} ({len(info['content'])} chars)",
            mimeType="text/plain"
        )
        for doc_id, info in documents.items()
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read document content."""
    if uri.startswith("document://"):
        doc_id = uri.replace("document://", "")
        if doc_id in documents:
            return documents[doc_id]['content']
    raise ValueError(f"Resource not found: {uri}")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="upload_document",
            description="Upload and store a document for RAG context",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Document name"},
                    "content": {"type": "string", "description": "Document content"}
                },
                "required": ["name", "content"]
            }
        ),
        Tool(
            name="get_rag_context",
            description="Get relevant context from uploaded documents for a query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "User query to find relevant context for"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="save_conversation",
            description="Save conversation history",
            inputSchema={
                "type": "object",
                "properties": {
                    "conversation": {"type": "array", "description": "Conversation messages"}
                },
                "required": ["conversation"]
            }
        ),
        Tool(
            name="list_documents",
            description="List all uploaded documents",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    """Handle tool calls."""
    if name == "upload_document":
        doc_id = f"doc_{len(documents) + 1}"
        documents[doc_id] = {
            'name': arguments['name'],
            'content': arguments['content']
        }
        return [TextContent(type="text", text=f"Document uploaded successfully with ID: {doc_id}")]
    
    elif name == "get_rag_context":
        query = arguments['query'].lower()
        context_parts = []
        
        for doc_id, doc_info in documents.items():
            content = doc_info['content'].lower()
            # Simple keyword matching for relevance
            if any(word in content for word in query.split()):
                # Get relevant snippets (simple approach)
                lines = doc_info['content'].split('\n')
                relevant_lines = [line for line in lines if any(word.lower() in line.lower() for word in query.split())]
                if relevant_lines:
                    context_parts.append(f"From {doc_info['name']}:\n" + '\n'.join(relevant_lines[:5]))
        
        context = '\n\n'.join(context_parts) if context_parts else "No relevant context found."
        return [TextContent(type="text", text=context)]
    
    elif name == "save_conversation":
        conversations.append(arguments['conversation'])
        return [TextContent(type="text", text=f"Conversation saved. Total saved: {len(conversations)}")]
    
    elif name == "list_documents":
        if not documents:
            return [TextContent(type="text", text="No documents uploaded yet.")]
        
        doc_list = []
        for doc_id, info in documents.items():
            doc_list.append(f"- {info['name']} (ID: {doc_id}, {len(info['content'])} characters)")
        
        return [TextContent(type="text", text="Uploaded documents:\n" + '\n'.join(doc_list))]
    
    raise ValueError(f"Unknown tool: {name}")

async def main():
    # MCP server stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="dual-chatbot-platform",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())