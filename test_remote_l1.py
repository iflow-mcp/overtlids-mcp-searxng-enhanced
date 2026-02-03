#!/usr/bin/env python3
"""简化版L1测试"""
import asyncio
import os
import json

async def test_uvx():
    # 测试配置
    command = "uvx"
    args = ["iflow-mcp-overtlids-mcp-searxng-enhanced"]
    env = os.environ.copy()
    env["SEARXNG_ENGINE_API_BASE_URL"] = "http://httpbin.org/search"

    print(f"启动命令: {command} {' '.join(args)}")
    print(f"环境变量: SEARXNG_ENGINE_API_BASE_URL={env['SEARXNG_ENGINE_API_BASE_URL']}")

    # 启动服务器
    proc = await asyncio.create_subprocess_exec(
        command, *args,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env
    )

    # 等待服务器启动
    await asyncio.sleep(2)

    # 发送初始化请求
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

    # 读取响应
    response_line = await asyncio.wait_for(proc.stdout.readline(), timeout=30)
    if response_line:
        response = json.loads(response_line.decode().strip())
        print("初始化响应:", json.dumps(response, indent=2))

        if "result" in response:
            print("✅ 初始化成功")
        else:
            print("❌ 初始化失败")
            proc.terminate()
            await proc.wait()
            return False

    # 发送list_tools请求
    list_tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }

    proc.stdin.write((json.dumps(list_tools_request) + "\n").encode())
    await proc.stdin.drain()

    # 读取响应
    response_line = await asyncio.wait_for(proc.stdout.readline(), timeout=30)
    if response_line:
        response = json.loads(response_line.decode().strip())
        print("List tools响应:", json.dumps(response, indent=2))

        if "result" in response and "tools" in response["result"]:
            tools = response["result"]["tools"]
            print(f"✅ 成功获取到 {len(tools)} 个工具")
            proc.terminate()
            await proc.wait()
            return True
        else:
            print("❌ 获取工具列表失败")
            proc.terminate()
            await proc.wait()
            return False

    proc.terminate()
    await proc.wait()
    return False

if __name__ == "__main__":
    result = asyncio.run(test_uvx())
    print(f"\n测试结果: {'成功' if result else '失败'}")
    exit(0 if result else 1)