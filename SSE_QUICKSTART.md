# SSE 模式快速配置

## ✅ SSE 服务器已成功配置！

### 🚀 启动 SSE 服务器

#### 方法1：使用 Python 脚本
```bash
cd /Users/xiaocan/MCP_Project
source .venv/bin/activate
python start_sse_server.py
```

#### 方法2：使用 Shell 脚本
```bash
cd /Users/xiaocan/MCP_Project
./start_sse.sh
```

#### 方法3：直接使用 tourmcp.py
```bash
cd /Users/xiaocan/MCP_Project
source .venv/bin/activate
python tourmcp.py --sse
```

### 📡 服务器信息

启动成功后，你会看到：

```
🚀 启动 MCP 服务器 (SSE模式)
   传输协议: Server-Sent Events (SSE)
   工具数量: 12

💡 Claude Desktop 配置示例:
   {"url": "http://localhost:8000/sse"}

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

服务器地址：`http://127.0.0.1:8000`  
SSE 端点：`http://127.0.0.1:8000/sse`

### ⚙️ Claude Desktop 配置

1. **找到配置文件**  
   macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. **添加 SSE 服务器配置**

   编辑配置文件，添加：
   
   ```json
   {
     "mcpServers": {
       "tour-guide-sse": {
         "url": "http://localhost:8000/sse"
       }
     }
   }
   ```

3. **重启 Claude Desktop**

   完全退出并重新启动 Claude Desktop

### ✅ 验证配置

在 Claude Desktop 中询问：

```
"帮我查询杭州的景点信息"
```

Claude 应该能够调用 `get_spots_by_city` 工具。

### 🔄 STDIO vs SSE 模式

| 模式 | 配置方式 | 适用场景 |
|------|---------|---------|
| STDIO | `command` + `args` | 本地使用，自动启动 |
| SSE | `url` | 远程访问，独立运行 |

**STDIO 配置示例：**
```json
{
  "mcpServers": {
    "tour-guide-stdio": {
      "command": "/Users/xiaocan/MCP_Project/.venv/bin/python",
      "args": ["/Users/xiaocan/MCP_Project/tourmcp.py"]
    }
  }
}
```

**SSE 配置示例：**
```json
{
  "mcpServers": {
    "tour-guide-sse": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

### 📝 注意事项

1. **SSE 模式需要先启动服务器**  
   在启动 Claude Desktop 之前，确保 SSE 服务器正在运行

2. **端口默认为 8000**  
   FastMCP 框架会自动选择端口，默认为 8000

3. **停止服务器**  
   在运行服务器的终端按 `Ctrl+C`

### 🛠️ 故障排除

#### 问题：端口被占用
```bash
# 查找占用 8000 端口的进程
lsof -i :8000

# 终止进程
kill -9 <PID>
```

#### 问题：无法连接
- 确认服务器正在运行
- 检查防火墙设置
- 验证配置文件中的 URL

#### 问题：Claude Desktop 无法识别工具
- 重启 Claude Desktop
- 检查配置文件 JSON 格式
- 查看 Claude Desktop 日志

### 📖 更多信息

- 完整 SSE 配置：[SSE_SETUP.md](SSE_SETUP.md)
- STDIO 配置：[CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md)
- 项目文档：[README.md](README.md)

---

**测试状态**: ✅ SSE 服务器成功启动在 http://127.0.0.1:8000
