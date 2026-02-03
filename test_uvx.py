#!/usr/bin/env python3
"""测试uvx包"""
import asyncio
import json
import os

async def test_uvx():
    # 测试配置
    command = "uvx"
    args = ["iflow-mcp-overtlids-mcp-searxng-enhanced"]
    env = os.environ.copy()
    env["SEARXNG_ENGINE_API_BASE_URL"] = "http://httpbin.org/search"

    print(f"🚀 启动命令: {command} {' '.join(args)}")
    print(f"🔧 环境变量: SEARXNG_ENGINE_API_BASE_URL={env['SEARXNG_ENGINE_API_BASE_URL']}")

    # 启动服务器
    proc = await asyncio.create_subprocess_exec(
        command, *args,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env
    )

    print("⏳ 等待服务器启动...")
    await asyncio.sleep(3)

    # 检查进程状态
    if proc.returncode is not None:
        stderr = await proc.stderr.read()
        print(f"❌ 服务器启动失败: {stderr.decode()}")
        return False

    print("✅ 服务器启动成功")

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

    print("📤 发送初始化请求...")
    proc.stdin.write((json.dumps(init_request) + "\n").encode())
    await proc.stdin.drain()

    # 读取响应
    try:
        response_line = await asyncio.wait_for(proc.stdout.readline(), timeout=30)
        if response_line:
            response = json.loads(response_line.decode().strip())
            if "result" in response:
                print("✅ 初始化成功")
            else:
                print(f"❌ 初始化失败: {response}")
                proc.terminate()
                await proc.wait()
                return False
    except asyncio.TimeoutError:
        print("❌ 初始化请求超时")
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

    print("📤 发送list_tools请求...")
    proc.stdin.write((json.dumps(list_tools_request) + "\n").encode())
    await proc.stdin.drain()

    # 读取响应
    try:
        response_line = await asyncio.wait_for(proc.stdout.readline(), timeout=30)
        if response_line:
            response = json.loads(response_line.decode().strip())
            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                print(f"✅ 成功获取到 {len(tools)} 个工具:")
                for tool in tools:
                    print(f"   - {tool['name']}")
                proc.terminate()
                await proc.wait()
                return True
            else:
                print(f"❌ 获取工具列表失败: {response}")
                proc.terminate()
                await proc.wait()
                return False
    except asyncio.TimeoutError:
        print("❌ list_tools请求超时")
        proc.terminate()
        await proc.wait()
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(test_uvx())
        print(f"\n🎉 测试结果: {'成功' if result else '失败'}")
        exit(0 if result else 1)
    except Exception as e:
        print(f"\n💥 测试异常: {e}")
        exit(1)