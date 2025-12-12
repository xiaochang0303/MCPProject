# MCP SSE 协议配置指南

## SSE 模式介绍

SSE (Server-Sent Events) 模式允许 MCP 服务器作为独立的 HTTP 服务运行，通过网络访问工具。

### SSE vs STDIO 模式对比

| 特性 | STDIO 模式 | SSE 模式 |
|------|-----------|----------|
| 传输方式 | 标准输入/输出 | HTTP + Server-Sent Events |
| 启动方式 | Claude Desktop 启动进程 | 独立运行服务器 |
| 网络访问 | 不支持 | 支持 |
| 多客户端 | 不支持 | 支持 |
| 调试 | 较难 | 易于调试（浏览器访问）|
| 适用场景 | 本地单用户 | 远程访问、多用户 |

## 启动 SSE 服务器

### 方法1：使用 Python 脚本

```bash
# 激活虚拟环境
source .venv/bin/activate

# 启动 SSE 服务器（默认端口 8000）
python start_sse_server.py

# 或指定端口
MCP_PORT=8080 python start_sse_server.py
```

### 方法2：使用 Shell 脚本

```bash
# 直接运行
./start_sse.sh

# 或指定端口
MCP_PORT=8080 ./start_sse.sh
```

### 方法3：使用 tourmcp.py 直接启动

```bash
# SSE 模式
python tourmcp.py --sse

# 或通过环境变量
MCP_TRANSPORT=sse python tourmcp.py

# 指定端口和主机
MCP_PORT=8080 MCP_HOST=127.0.0.1 python tourmcp.py --sse
```

## Claude Desktop 配置

### SSE 模式配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tour-guide-sse": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

### 多服务器混合配置

可以同时配置 STDIO 和 SSE 模式：

```json
{
  "mcpServers": {
    "tour-guide-stdio": {
      "command": "/Users/xiaocan/MCP_Project/.venv/bin/python",
      "args": ["/Users/xiaocan/MCP_Project/tourmcp.py"],
      "cwd": "/Users/xiaocan/MCP_Project"
    },
    "tour-guide-sse": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

## 环境变量配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MCP_TRANSPORT` | `stdio` | 传输模式：`stdio` 或 `sse` |
| `MCP_PORT` | `8000` | SSE 服务器端口 |
| `MCP_HOST` | `0.0.0.0` | SSE 服务器监听地址 |

### 示例：自定义配置

```bash
# 端口 8080，只监听本地
MCP_PORT=8080 MCP_HOST=127.0.0.1 python start_sse_server.py
```

## 验证 SSE 服务器

### 1. 启动服务器

```bash
./start_sse.sh
```

输出应该显示：

```
======================================================================
  🚀 旅游景点数据 MCP 服务器 (SSE 模式)
======================================================================

📡 服务器信息:
   地址: http://0.0.0.0:8000
   SSE端点: http://0.0.0.0:8000/sse
   传输协议: Server-Sent Events

💡 提示:
   - 在浏览器访问: http://localhost:8000/sse
   - 按 Ctrl+C 停止服务器
```

### 2. 测试连接

在浏览器中访问：
```
http://localhost:8000/sse
```

或使用 curl：
```bash
curl http://localhost:8000/sse
```

### 3. 配置 Claude Desktop

1. 确保 SSE 服务器正在运行
2. 编辑 Claude Desktop 配置文件
3. 重启 Claude Desktop
4. 验证工具是否可用

## 网络配置

### 允许远程访问

如果需要从其他机器访问（例如局域网内其他设备）：

```bash
# 监听所有网络接口
MCP_HOST=0.0.0.0 MCP_PORT=8000 ./start_sse.sh
```

然后在 Claude Desktop 配置中使用服务器 IP：

```json
{
  "mcpServers": {
    "tour-guide-sse": {
      "url": "http://192.168.1.100:8000/sse"
    }
  }
}
```

### 防火墙配置

如果启用了防火墙，需要允许端口访问：

**macOS:**
```bash
# 系统偏好设置 -> 安全性与隐私 -> 防火墙 -> 防火墙选项
# 允许 Python 传入连接
```

**Linux (UFW):**
```bash
sudo ufw allow 8000/tcp
```

## 生产部署建议

### 1. 使用反向代理 (Nginx)

```nginx
server {
    listen 80;
    server_name tour-mcp.example.com;

    location /sse {
        proxy_pass http://localhost:8000/sse;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        
        # SSE 特定配置
        proxy_buffering off;
        proxy_read_timeout 24h;
    }
}
```

### 2. 使用 systemd 服务 (Linux)

创建 `/etc/systemd/system/tour-mcp.service`:

```ini
[Unit]
Description=Tour MCP SSE Server
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/MCP_Project
Environment="MCP_TRANSPORT=sse"
Environment="MCP_PORT=8000"
Environment="MCP_HOST=127.0.0.1"
ExecStart=/path/to/MCP_Project/.venv/bin/python start_sse_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl enable tour-mcp
sudo systemctl start tour-mcp
sudo systemctl status tour-mcp
```

### 3. 使用 Docker

创建 `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir fastmcp matplotlib

ENV MCP_TRANSPORT=sse
ENV MCP_PORT=8000
ENV MCP_HOST=0.0.0.0

EXPOSE 8000

CMD ["python", "start_sse_server.py"]
```

构建和运行：
```bash
docker build -t tour-mcp .
docker run -p 8000:8000 tour-mcp
```

## 故障排除

### 问题1：端口被占用

**错误**: `Address already in use`

**解决**:
```bash
# 查找占用端口的进程
lsof -i :8000

# 终止进程或使用其他端口
MCP_PORT=8001 ./start_sse.sh
```

### 问题2：无法连接

**检查清单**:
- [ ] SSE 服务器是否正在运行
- [ ] 端口是否正确
- [ ] 防火墙是否允许
- [ ] Claude Desktop 配置是否正确

**测试命令**:
```bash
# 测试本地连接
curl http://localhost:8000/sse

# 测试远程连接
curl http://服务器IP:8000/sse
```

### 问题3：Claude Desktop 无法连接

**解决步骤**:
1. 确认 SSE 服务器正在运行
2. 在浏览器测试 URL 是否可访问
3. 检查 Claude Desktop 配置文件 JSON 格式
4. 重启 Claude Desktop
5. 查看 Claude Desktop 日志

## 性能优化

### 1. 调整超时设置

```python
# 在 tourmcp.py 中
mcp.run(
    transport="sse",
    port=8000,
    host="0.0.0.0",
    timeout=300  # 5分钟超时
)
```

### 2. 日志配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 3. 监控和健康检查

添加健康检查端点：
```python
@mcp.tool()
def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "tools_count": 12
    }
```

## 安全建议

1. **使用 HTTPS**: 在生产环境使用反向代理配置 SSL
2. **访问控制**: 添加认证机制
3. **限制访问**: 只监听 127.0.0.1 或使用防火墙
4. **日志审计**: 记录所有工具调用
5. **更新依赖**: 定期更新 fastmcp 和其他依赖

## 监控脚本

创建简单的监控脚本：

```bash
#!/bin/bash
# monitor_sse.sh

while true; do
    if curl -f http://localhost:8000/sse > /dev/null 2>&1; then
        echo "[$(date)] ✅ SSE server is running"
    else
        echo "[$(date)] ❌ SSE server is down"
        # 可以添加重启逻辑
    fi
    sleep 60
done
```

## 快速参考

### 启动命令
```bash
# 开发环境
./start_sse.sh

# 生产环境
MCP_HOST=127.0.0.1 MCP_PORT=8000 python start_sse_server.py
```

### 测试命令
```bash
# 测试连接
curl http://localhost:8000/sse

# 查看日志
tail -f /var/log/tour-mcp.log
```

### Claude Desktop 配置
```json
{
  "mcpServers": {
    "tour-guide-sse": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

---

**提示**: SSE 模式特别适合需要远程访问或多用户场景。对于本地单用户使用，STDIO 模式更简单。
