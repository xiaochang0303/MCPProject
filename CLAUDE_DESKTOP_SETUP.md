# Claude Desktop 配置指南

## 将旅游MCP工具集成到Claude Desktop

本项目支持两种连接模式：
- **STDIO 模式**：Claude Desktop 直接启动 Python 进程（推荐本地使用）
- **SSE 模式**：通过 HTTP 连接到独立运行的服务器（支持远程访问）

> 📖 **SSE 详细配置**: 查看 [SSE_SETUP.md](SSE_SETUP.md) 了解 SSE 模式的完整配置

---

## 方式一：STDIO 模式（本地进程）

### 第一步：找到配置文件

Claude Desktop的配置文件位于：

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### 第二步：编辑配置文件

打开或创建 `claude_desktop_config.json`，添加以下配置：

#### STDIO 模式配置（默认）

```json
{
  "mcpServers": {
    "tour-guide": {
      "command": "/Users/xiaocan/MCP_Project/.venv/bin/python",
      "args": ["/Users/xiaocan/MCP_Project/tourmcp.py"],
      "cwd": "/Users/xiaocan/MCP_Project",
      "env": {
        "PYTHONPATH": "/Users/xiaocan/MCP_Project"
      }
    }
  }
}
```

> ⚠️ **重要**: 请将路径替换为你的实际项目路径

---

## 方式二：SSE 模式（HTTP 服务器）

### 第一步：启动 SSE 服务器

```bash
# 进入项目目录
cd /Users/xiaocan/MCP_Project

# 启动 SSE 服务器
./start_sse.sh

# 或使用 Python 脚本
python start_sse_server.py
```

服务器启动后会显示：
```
🚀 旅游景点数据 MCP 服务器 (SSE 模式)
地址: http://0.0.0.0:8000
SSE端点: http://0.0.0.0:8000/sse
```

### 第二步：配置 Claude Desktop

编辑 `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tour-guide-sse": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

### SSE 模式优势

- ✅ 支持远程访问
- ✅ 服务器独立运行
- ✅ 易于调试（浏览器可访问）
- ✅ 支持多个客户端连接
- ✅ 适合生产环境部署

> 📖 完整的 SSE 配置和部署说明请查看 [SSE_SETUP.md](SSE_SETUP.md)

---

## 第三步（通用）：重启Claude Desktop

保存配置文件后，完全退出并重新启动 Claude Desktop。

> **注意**: 如果使用 SSE 模式，请确保服务器在启动 Claude Desktop 之前已经运行

### 第四步（通用）：验证连接

在 Claude Desktop 中，你应该能看到以下工具可用：

#### 数据检索工具
- `get_spots_by_province` - 获取省份景点
- `get_spots_by_city` - 获取城市景点
- `get_spots_by_cities` - 批量获取

#### 可视化工具
- `visualize_city_ratings` - 景点评分可视化
- `visualize_spots_comparison` - 城市对比
- `get_spots_statistics` - 统计信息

#### 内容生成工具
- `generate_xiaohongshu_content` - 生成小红书内容
- `publish_xiaohongshu_video` - 发布视频
- `publish_xiaohongshu_images` - 发布图文
- `batch_publish_xiaohongshu` - 批量发布

#### 其他工具
- `plan_trip` - 旅游规划
- `scenic_resource` - 资源访问

## 使用示例

在 Claude Desktop 中，你可以这样使用：

### 示例1：查询景点
```
"帮我查询杭州的景点信息"
```

Claude 会自动调用 `get_spots_by_city` 工具。

### 示例2：生成内容
```
"帮我生成一篇关于舟山的小红书旅游攻略"
```

Claude 会调用 `generate_xiaohongshu_content` 工具。

### 示例3：数据分析
```
"对比浙江省杭州、宁波、舟山三个城市的景点情况"
```

Claude 会调用 `visualize_spots_comparison` 工具。

## 故障排除

### 问题1：工具不显示

**原因**: 配置文件路径错误或格式错误

**解决**:
1. 检查配置文件路径是否正确
2. 验证JSON格式是否有效（使用在线JSON验证器）
3. 确保Python虚拟环境路径正确

### 问题2：工具调用失败

**原因**: 依赖未安装或数据文件缺失

**解决**:
```bash
# 激活虚拟环境
source /Users/xiaocan/MCP_Project/.venv/bin/activate

# 安装依赖
pip install fastmcp matplotlib

# 验证工具
python verify_mcp_tools.py
```

### 问题3：权限错误

**原因**: Python脚本没有执行权限

**解决**:
```bash
chmod +x /Users/xiaocan/MCP_Project/tourmcp.py
```

## 高级配置

### 使用不同的Python环境

如果你想使用系统Python或其他虚拟环境：

```json
{
  "mcpServers": {
    "tour-guide": {
      "command": "/path/to/your/python",
      "args": ["/path/to/tourmcp.py"],
      "cwd": "/path/to/MCP_Project"
    }
  }
}
```

### 添加环境变量

如果需要设置额外的环境变量：

```json
{
  "mcpServers": {
    "tour-guide": {
      "command": "/Users/xiaocan/MCP_Project/.venv/bin/python",
      "args": ["/Users/xiaocan/MCP_Project/tourmcp.py"],
      "cwd": "/Users/xiaocan/MCP_Project",
      "env": {
        "PYTHONPATH": "/Users/xiaocan/MCP_Project",
        "DATA_ROOT": "./data",
        "DEBUG": "true"
      }
    }
  }
}
```

### 同时配置多个MCP服务器

```json
{
  "mcpServers": {
    "tour-guide": {
      "command": "/Users/xiaocan/MCP_Project/.venv/bin/python",
      "args": ["/Users/xiaocan/MCP_Project/tourmcp.py"],
      "cwd": "/Users/xiaocan/MCP_Project"
    },
    "other-server": {
      "command": "node",
      "args": ["/path/to/other/server.js"]
    }
  }
}
```

## 验证安装

### 手动测试服务器

在启动Claude Desktop之前，可以手动测试MCP服务器：

```bash
# 激活虚拟环境
cd /Users/xiaocan/MCP_Project
source .venv/bin/activate

# 运行服务器（测试模式）
python tourmcp.py

# 或运行验证脚本
python verify_mcp_tools.py
```

### 检查日志

Claude Desktop的日志通常位于：

**macOS:**
```
~/Library/Logs/Claude/
```

查找与MCP相关的错误信息。

## 更新工具

当你更新了 `tourmcp.py` 中的工具后：

1. 保存文件
2. 重启 Claude Desktop
3. 新工具将自动可用

不需要修改配置文件，除非改变了文件路径。

## 最佳实践

1. **版本控制**: 使用git管理你的MCP工具代码
2. **测试优先**: 更新工具后先运行 `verify_mcp_tools.py`
3. **文档同步**: 更新工具时同步更新README
4. **错误处理**: 确保工具有完善的错误处理
5. **日志记录**: 在工具中添加适当的日志输出

## 资源链接

- [MCP官方文档](https://modelcontextprotocol.io/)
- [FastMCP文档](https://github.com/jlowin/fastmcp)
- [项目README](README.md)
- [快速开始指南](QUICKSTART.md)

## 获取帮助

如果遇到问题：

1. 查看 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) 了解项目详情
2. 运行 `python verify_mcp_tools.py` 诊断问题
3. 检查Claude Desktop日志文件
4. 确认所有依赖已正确安装

---

**配置完成后，你就可以在Claude Desktop中直接使用这些旅游数据工具了！** 🎉
