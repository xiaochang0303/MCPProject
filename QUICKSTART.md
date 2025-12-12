# 快速开始指南

## 🚀 5分钟快速上手

### 第一步：查看数据

```python
from tourmcp import get_spots_by_city

# 获取城市景点
data = get_spots_by_city("浙江", "杭州")
print(f"找到 {data['count']} 个景点")
```

### 第二步：生成内容

```python
from tourmcp import generate_xiaohongshu_content

# 自动生成小红书内容
content = generate_xiaohongshu_content(
    province="浙江",
    city="杭州",
    style="旅游攻略"
)

print(content['title'])
print(content['content'])
```

### 第三步：发布笔记（可选）

```python
from tourmcp import publish_xiaohongshu_images

# 发布图文笔记
result = publish_xiaohongshu_images(
    file_path="/path/to/photo.jpg",
    title=content['title'],
    content=content['content'],
    topics=content['topics']
)
```

## 🎯 常用场景

### 场景1：查看景点统计

```python
from tourmcp import get_spots_statistics

stats = get_spots_statistics("浙江", "杭州")
print(f"总景点: {stats['statistics']['total_spots']}")
print(f"平均评分: {stats['statistics']['avg_rating']}")
```

### 场景2：对比多个城市

```python
from tourmcp import visualize_spots_comparison

comparison = visualize_spots_comparison(
    "浙江",
    ["杭州", "宁波", "舟山"],
    output_format="data"
)

for city in comparison['data']:
    print(f"{city['city']}: {city['count']}个景点")
```

### 场景3：批量发布

```python
from tourmcp import batch_publish_xiaohongshu

result = batch_publish_xiaohongshu(
    province="浙江",
    cities=["杭州", "宁波", "舟山"],
    file_paths=[
        "/path/to/hangzhou.jpg",
        "/path/to/ningbo.jpg",
        "/path/to/zhoushan.jpg"
    ],
    style="旅游攻略"
)

print(f"成功: {result['success_count']} 篇")
```

## 🔧 安装配置

### 基础功能（数据查询、内容生成）

```bash
pip install fastmcp
```

### 完整功能（包括发布）

```bash
pip install fastmcp matplotlib selenium
```

## 📝 作为 MCP 服务器运行

```bash
# 启动 MCP 服务器
python tourmcp.py

# 然后在 Claude Desktop 中配置该服务器
# 配置文件路径: ~/Library/Application Support/Claude/claude_desktop_config.json
```

配置示例：
```json
{
  "mcpServers": {
    "tour-guide": {
      "command": "python",
      "args": ["/path/to/tourmcp.py"],
      "cwd": "/path/to/MCP_Project"
    }
  }
}
```

## 📚 更多信息

- 完整文档：[README.md](README.md)
- 完整演示：运行 `python demo_complete_workflow.py`
- 测试工具：运行 `python test_xiaohongshu_tools.py`

## 💡 提示

- 首次使用发布功能需要手动登录小红书
- 支持定时发布，避免频繁发帖
- 可以只使用内容生成功能，手动复制到小红书
- 所有工具都返回结构化数据，方便集成
