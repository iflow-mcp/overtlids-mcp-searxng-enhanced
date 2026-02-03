#!/usr/bin/env python3
"""Simple MCP Server Test"""
import asyncio
import json
import sys
import os

async def test_mcp():
    # Set environment variables
    env = os.environ.copy()
    env["SEARXNG_ENGINE_API_BASE_URL"] = "http://httpbin.org/search"
    
    # Start the MCP server
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "mcp_server.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
        cwd="/app/auto-mcp-upload/data/2804"
    )
    
    # Wait for server to start
    await asyncio.sleep(2)
    
    # Send initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "test", "version": "1.0"}
        }
    }
    
    proc.stdin.write((json.dumps(init_request) + "\n").encode())
    await proc.stdin.drain()
    
    # Read response
    response_line = await proc.stdout.readline()
    if response_line:
        print("Initialize response:", response_line.decode().strip())
    
    # Send list_tools request
    list_tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    proc.stdin.write((json.dumps(list_tools_request) + "\n").encode())
    await proc.stdin.drain()
    
    # Read response
    response_line = await proc.stdout.readline()
    if response_line:
        response = json.loads(response_line.decode().strip())
        print("List tools response:", json.dumps(response, indent=2))
        
        if "result" in response and "tools" in response["result"]:
            tools = response["result"]["tools"]
            print(f"\n✅ 成功获取到 {len(tools)} 个工具:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool.get('description', 'N/A')}")
    
    # Cleanup
    proc.terminate()
    await proc.wait()

if __name__ == "__main__":
    asyncio.run(test_mcp())