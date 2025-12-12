#!/usr/bin/env python3
"""
MCP 服务器 SSE 模式启动脚本
使用 Server-Sent Events (SSE) 协议运行 MCP 服务器
"""

import sys
import os

# 添加项目路径到 Python 路径
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# 设置环境变量
os.environ["MCP_TRANSPORT"] = "sse"
os.environ["MCP_PORT"] = os.getenv("MCP_PORT", "8000")
os.environ["MCP_HOST"] = os.getenv("MCP_HOST", "0.0.0.0")

if __name__ == "__main__":
    from tourmcp import mcp
    
    print("="*70)
    print("  🚀 旅游景点数据 MCP 服务器 (SSE 模式)")
    print("="*70)
    print(f"\n📡 服务器信息:")
    print(f"   传输协议: Server-Sent Events (SSE)")
    print(f"   默认端口: 由 FastMCP 框架管理")
    print(f"\n🔧 可用工具: 12个")
    print("   - 数据检索: 3个")
    print("   - 可视化: 3个")
    print("   - 小红书发布: 4个")
    print("   - 其他: 2个")
    print(f"\n💡 提示:")
    print(f"   - FastMCP 会自动选择可用端口")
    print(f"   - 查看启动日志获取实际访问地址")
    print(f"   - 按 Ctrl+C 停止服务器")
    print(f"\n📖 Claude Desktop 配置示例:")
    print('   {"url": "http://localhost:8000/sse"}')
    print("\n" + "="*70 + "\n")
    
    try:
        mcp.run(transport="sse")
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
