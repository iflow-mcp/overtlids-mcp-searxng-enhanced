#!/usr/bin/env python3
"""
MCP Server entry point for uvx
"""
import asyncio
import sys
from mcp_server import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        sys.exit(1)