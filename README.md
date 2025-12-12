# 旅游景点数据 MCP 工具

这个项目提供了一套 MCP (Model Context Protocol) 工具，用于检索和可视化中国景点数据。

> 📖 **快速开始**: 查看 [QUICKSTART.md](QUICKSTART.md) 快速上手  
> 🎬 **完整演示**: 运行 `python demo_complete_workflow.py` 查看所有功能  
> 🔧 **STDIO 配置**: 查看 [CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md)  
> 🌐 **SSE 配置**: 查看 [SSE_SETUP.md](SSE_SETUP.md) 使用 HTTP 服务器模式

## 功能特点

### 数据检索工具

1. **get_spots_by_province** - 获取指定省份的所有景点数据
2. **get_spots_by_city** - 获取指定城市的景点数据
3. **get_spots_by_cities** - 批量获取多个城市的景点数据

### 可视化工具

4. **visualize_city_ratings** - 生成城市景点评分可视化
   - 支持返回数据格式（适合进一步处理）
   - 支持返回 Base64 编码的 PNG 图片（可直接显示）

5. **visualize_spots_comparison** - 生成多城市对比可视化
   - 对比多个城市的景点数量
   - 对比多个城市的平均评分
   
6. **get_spots_statistics** - 获取景点统计信息
   - 总景点数
   - 平均评分、最高/最低评分
   - 评分分布
   - Top 5 高评分景点

### 智能提示词工具

7. **plan_trip** - 生成旅游路线规划提示词

### 资源协议

8. **scenic_resource** - 使用 `scenic://` 协议访问景点数据

### 小红书发布工具

9. **generate_xiaohongshu_content** - 根据景点数据自动生成小红书笔记内容
   - 支持多种风格：旅游攻略、Vlog、打卡分享
   - 自动选择高评分景点
   - 生成吸引人的标题和话题标签

10. **publish_xiaohongshu_video** - 发布视频笔记到小红书
    - 支持定时发布
    - 自动添加话题标签
    - 需要浏览器自动化环境

11. **publish_xiaohongshu_images** - 发布图文笔记到小红书
    - 支持单图或多图发布
    - 自动填充标题和内容
    - 智能话题推荐

12. **batch_publish_xiaohongshu** - 批量发布小红书笔记
    - 支持多个城市批量发布
    - 自动计算发布间隔
    - 统一内容风格

## 安装依赖

### 基础依赖

```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装必需的依赖
pip install fastmcp matplotlib

# 或者使用 uv（如果已安装）
uv pip install fastmcp matplotlib
```

### 小红书发布功能依赖（可选）

如果需要使用小红书发布功能，需要额外安装：

```bash
# 安装 selenium 用于浏览器自动化
pip install selenium

# 安装浏览器驱动（选择一个）
# Chrome: 下载 ChromeDriver (https://chromedriver.chromium.org/)
# Firefox: 下载 GeckoDriver (https://github.com/mozilla/geckodriver/releases)
```

## 使用示例

### 1. 作为 MCP 服务器运行

```bash
python tourmcp.py
```

### 2. 在 Python 代码中使用

```python
from tourmcp import (
    get_spots_by_city,
    visualize_city_ratings,
    visualize_spots_comparison,
    get_spots_statistics
)

# 获取城市景点数据
data = get_spots_by_city("浙江", "杭州")
print(f"找到 {data['count']} 个景点")

# 生成评分可视化数据
viz_data = visualize_city_ratings("浙江", "杭州", output_format="data")
print(viz_data)

# 生成 Base64 图片
viz_image = visualize_city_ratings("浙江", "杭州", output_format="image")
if viz_image['success']:
    # 可以将 viz_image['image_base64'] 发送到前端显示
    print(f"图片生成成功，大小: {len(viz_image['image_base64'])} 字节")

# 对比多个城市
comparison = visualize_spots_comparison(
    "浙江",
    ["杭州", "宁波", "舟山"],
    output_format="data"
)

# 获取统计信息
stats = get_spots_statistics("浙江", "杭州")
print(f"平均评分: {stats['statistics']['avg_rating']}")
```

### 3. 运行测试

```bash
# 测试基本功能
python test.py

# 测试可视化工具
python test_visualization_tools.py

# 测试小红书内容生成
python test_xiaohongshu_tools.py
```

### 4. 使用小红书发布功能

```python
from tourmcp import (
    generate_xiaohongshu_content,
    publish_xiaohongshu_images,
    publish_xiaohongshu_video
)

# 1. 生成内容
content = generate_xiaohongshu_content(
    province="浙江",
    city="杭州",
    style="旅游攻略"  # 可选: "Vlog", "打卡分享"
)

print(f"标题: {content['title']}")
print(f"内容: {content['content']}")
print(f"话题: {content['topics']}")

# 2. 发布图文笔记（需要先登录小红书）
result = publish_xiaohongshu_images(
    file_path="/path/to/image.jpg",
    title=content['title'],
    content=content['content'],
    topics=content['topics'],
    schedule_hours=24  # 24小时后发布
)

print(f"发布结果: {result['message']}")

# 3. 批量发布
from tourmcp import batch_publish_xiaohongshu

batch_result = batch_publish_xiaohongshu(
    province="浙江",
    cities=["杭州", "宁波", "舟山"],
    file_paths=[
        "/path/to/hangzhou.jpg",
        "/path/to/ningbo.jpg",
        "/path/to/zhoushan.jpg"
    ],
    style="旅游攻略",
    schedule_interval_hours=24  # 每篇间隔24小时
)

print(f"成功发布: {batch_result['success_count']} 篇")
```

## MCP 工具详细说明

### 数据检索工具

#### get_spots_by_city

获取指定城市的景点数据。

**参数:**
- `province` (str): 省份名称
- `city` (str): 城市名称

**返回示例:**
```json
{
  "province": "浙江",
  "city": "杭州",
  "spots": [...],
  "count": 50
}
```

### 可视化工具

#### visualize_city_ratings

**参数:**
- `province` (str): 省份名称
- `city` (str): 城市名称
- `output_format` (str): 输出格式，"data" 或 "image"

**返回示例 (data 格式):**
```json
{
  "success": true,
  "province": "浙江",
  "city": "杭州",
  "visualization_type": "ratings_bar_chart",
  "data": {
    "labels": ["西湖", "灵隐寺", ...],
    "values": [4.8, 4.6, ...]
  }
}
```

**返回示例 (image 格式):**
```json
{
  "success": true,
  "province": "浙江",
  "city": "杭州",
  "visualization_type": "ratings_bar_chart",
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "format": "png"
}
```

### visualize_spots_comparison

**参数:**
- `province` (str): 省份名称
- `cities` (List[str]): 城市名称列表
- `output_format` (str): 输出格式，"data" 或 "image"

**返回示例:**
```json
{
  "success": true,
  "province": "浙江",
  "visualization_type": "city_comparison",
  "data": [
    {
      "city": "杭州",
      "count": 50,
      "avg_rating": 4.5
    },
    ...
  ]
}
```

### get_spots_statistics

**参数:**
- `province` (str): 省份名称
- `city` (str, 可选): 城市名称（如果不提供，统计整个省份）

**返回示例:**
```json
{
  "success": true,
  "location": "杭州, 浙江",
  "statistics": {
    "total_spots": 50,
    "avg_rating": 4.5,
    "max_rating": 5.0,
    "min_rating": 3.2,
    "rating_distribution": {
      "5.0": 10,
      "4.0-4.9": 25,
      "3.0-3.9": 15,
      "2.0-2.9": 0,
      "< 2.0": 0
    },
    "top_rated_spots": [
      {"name": "西湖", "rating": 5.0},
      ...
    ]
  }
}
```

### 小红书发布工具

#### generate_xiaohongshu_content

根据景点数据自动生成小红书笔记内容。

**参数:**
- `province` (str): 省份名称
- `city` (str): 城市名称
- `spot_name` (str, 可选): 特定景点名称
- `style` (str): 内容风格，可选 "旅游攻略"、"Vlog"、"打卡分享"

**返回示例:**
```json
{
  "success": true,
  "title": "🌟杭州必去景点！3个宝藏打卡地分享✨",
  "content": "📍杭州旅游攻略来啦！\n\n1️⃣ 西湖...",
  "topics": ["#杭州旅游", "#旅游攻略", "#景点推荐"],
  "spots_included": ["西湖", "灵隐寺", "..."],
  "style": "旅游攻略"
}
```

#### publish_xiaohongshu_video

发布视频笔记到小红书。

**参数:**
- `file_path` (str): 视频文件绝对路径
- `title` (str): 笔记标题
- `content` (str): 笔记内容
- `topics` (List[str], 可选): 话题标签列表
- `schedule_hours` (int): 定时发布的小时数（默认24）

**返回示例:**
```json
{
  "success": true,
  "message": "视频笔记发布成功",
  "details": {
    "file_path": "/path/to/video.mp4",
    "title": "标题",
    "topics": ["#旅游", "#攻略"],
    "schedule_hours": 24
  }
}
```

**注意事项:**
- 首次使用需要手动登录小红书，会自动保存cookies
- 需要安装 selenium 和浏览器驱动
- 支持定时发布功能
- 会自动等待视频上传完成

#### publish_xiaohongshu_images

发布图文笔记到小红书。

**参数:**
- `file_path` (str): 图片文件绝对路径（支持多图）
- `title` (str): 笔记标题
- `content` (str): 笔记内容
- `topics` (List[str], 可选): 话题标签列表
- `schedule_hours` (int): 定时发布的小时数

**使用示例:**
```python
result = publish_xiaohongshu_images(
    file_path="/Users/user/Desktop/hangzhou.jpg",
    title="杭州西湖一日游",
    content="今天去了西湖，真的太美了！",
    topics=["#杭州", "#西湖", "#旅游"],
    schedule_hours=2  # 2小时后发布
)
```

#### batch_publish_xiaohongshu

批量发布多个城市的小红书笔记。

**参数:**
- `province` (str): 省份名称
- `cities` (List[str]): 城市列表
- `file_paths` (List[str]): 对应每个城市的媒体文件路径
- `style` (str): 内容风格
- `schedule_interval_hours` (int): 每篇笔记之间的发布间隔

**返回示例:**
```json
{
  "success": true,
  "total": 3,
  "success_count": 3,
  "failed_count": 0,
  "results": [
    {
      "city": "杭州",
      "success": true,
      "title": "...",
      "schedule_hours": 24
    },
    ...
  ]
}
```

**使用场景:**
- 旅游博主批量发布多个城市的内容
- 定时发布，避免一次性发太多
- 自动生成内容和话题标签

## 小红书发布功能配置

### 1. 首次使用设置

```bash
# 确保已安装依赖
pip install selenium

# 配置浏览器驱动路径（在 liulanqi.py 中）
# Chrome: 下载并配置 ChromeDriver
# Firefox: 下载并配置 GeckoDriver
```

### 2. Cookies 管理

首次运行会提示登录小红书，登录后 cookies 会自动保存到 `cookies/xiaohongshu.json`。
后续使用会自动加载保存的 cookies，无需重复登录。

### 3. 内容风格说明

| 风格 | 特点 | 适用场景 |
|------|------|----------|
| 旅游攻略 | 详细的景点介绍和游玩建议 | 深度游、攻略分享 |
| Vlog | 轻松的视频日记风格 | 视频博主、日常分享 |
| 打卡分享 | 简短的打卡记录 | 快速分享、图片集 |

### 4. 话题标签优化

工具会根据城市和风格自动生成相关话题标签，包括：
- 地理位置标签（如 #杭州旅游）
- 内容类型标签（如 #旅游攻略、#Vlog）
- 通用热门标签（如 #打卡、#周末游）

## 数据格式

景点 JSON 数据应放在 `./data` 目录下，按以下结构组织：

```
data/
├── 浙江/
│   ├── 杭州/
│   │   ├── 西湖/
│   │   │   └── scene_info.json
│   │   └── 灵隐寺/
│   │       └── scene_info.json
│   └── 舟山/
│       └── ...
└── 江苏/
    └── ...
```

每个 `scene_info.json` 应包含以下字段：
```json
{
  "name": "景点名称",
  "rating": 4.5,
  "热度": "高",
  "是否免费": false,
  ...
}
```

## 注意事项

1. 如果不安装 `matplotlib`，可视化工具仍可使用 `output_format="data"` 模式返回数据
2. 中文字体显示可能需要根据系统调整 `matplotlib` 配置
3. 生成的 Base64 图片可以直接在 HTML 中使用：`<img src="data:image/png;base64,{image_base64}">`

## 项目文件

- `tourmcp.py` - MCP 服务器和工具定义（包含所有工具）
- `upload_xiaohongshu.py` - 小红书发布的底层实现
- `liulanqi.py` - 浏览器自动化工具
- `test.py` - 基本功能测试
- `test_visualization_tools.py` - 可视化工具测试
- `test_xiaohongshu_tools.py` - 小红书内容生成测试
- `visualize_spots.py` - 独立的可视化脚本（已被 MCP 工具取代）

## 工作流程示例

### 完整的旅游内容发布流程

```python
from tourmcp import (
    get_spots_by_city,
    generate_xiaohongshu_content,
    publish_xiaohongshu_images,
    get_spots_statistics
)

# 1. 获取景点数据
spots_data = get_spots_by_city("浙江", "杭州")
print(f"找到 {spots_data['count']} 个景点")

# 2. 查看统计信息
stats = get_spots_statistics("浙江", "杭州")
print(f"平均评分: {stats['statistics']['avg_rating']}")
print(f"Top 景点: {stats['statistics']['top_rated_spots']}")

# 3. 生成小红书内容
content = generate_xiaohongshu_content(
    province="浙江",
    city="杭州",
    style="旅游攻略"
)

# 4. 发布到小红书（准备好图片文件）
result = publish_xiaohongshu_images(
    file_path="/path/to/hangzhou_photo.jpg",
    title=content['title'],
    content=content['content'],
    topics=content['topics']
)

print(f"发布结果: {result['message']}")
```

## 常见问题 (FAQ)

### Q: 如何更换小红书账号？
A: 删除 `cookies/xiaohongshu.json` 文件，重新运行工具时会要求登录。

### Q: 发布失败怎么办？
A: 检查以下几点：
1. Selenium 和浏览器驱动是否正确安装
2. Cookies 是否过期（删除后重新登录）
3. 小红书页面结构是否更新（可能需要更新选择器）
4. 网络连接是否正常

### Q: 支持哪些图片/视频格式？
A: 
- 图片: JPG, PNG
- 视频: MP4, MOV, AVI

### Q: 如何调整发布时间？
A: 使用 `schedule_hours` 参数设置延迟发布的小时数，例如 `schedule_hours=48` 表示48小时后发布。

### Q: 可以不使用自动化发布，只生成内容吗？
A: 可以！只使用 `generate_xiaohongshu_content` 工具生成内容，然后手动复制到小红书发布。

## License

MIT
