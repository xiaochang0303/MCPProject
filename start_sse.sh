#!/bin/bash

# MCP 服务器 SSE 模式启动脚本 (Shell版本)

# 设置颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 配置
export MCP_TRANSPORT="sse"
export MCP_PORT="${MCP_PORT:-8000}"
export MCP_HOST="${MCP_HOST:-0.0.0.0}"

echo -e "${BLUE}======================================================================${NC}"
echo -e "${GREEN}  🚀 旅游景点数据 MCP 服务器 (SSE 模式)${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""
echo -e "${YELLOW}📡 服务器信息:${NC}"
echo "   地址: http://${MCP_HOST}:${MCP_PORT}"
echo "   SSE端点: http://${MCP_HOST}:${MCP_PORT}/sse"
echo "   传输协议: Server-Sent Events"
echo ""
echo -e "${YELLOW}💡 提示:${NC}"
echo "   - 在浏览器访问: http://localhost:${MCP_PORT}/sse"
echo "   - 按 Ctrl+C 停止服务器"
echo ""
echo -e "${BLUE}======================================================================${NC}"
echo ""

# 激活虚拟环境（如果存在）
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# 启动服务器
python start_sse_server.py
