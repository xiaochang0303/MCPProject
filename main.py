from mcp.server.fastmcp import FastMCP
import os
import json
from typing import List, Dict, Any

mcp = FastMCP()

DATA_ROOT = "./data"   # 你的 JSON 数据根目录，例如：./data/浙江/舟山/朱家尖大青山景区/scene_info.json


def load_json_files_in_path(path: str) -> List[Dict[str, Any]]:
    """读取一个目录下所有 JSON 文件"""
    items = []
    if not os.path.exists(path):
        return items

    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(".json"):
                fp = os.path.join(root, f)
                try:
                    with open(fp, "r", encoding="utf-8") as fh:
                        data = json.load(fh)
                        items.append(data)
                except:
                    pass
    return items


@mcp.tool(
    name='get_spots_by_province',
    description='根据省份名称获取该省所有景点数据（从本地JSON文件读取）'
)
def get_spots_by_province(province: str) -> Dict[str, Any]:
    target_path = os.path.join(DATA_ROOT, province)

    result = load_json_files_in_path(target_path)
    
    return {
        "province": province,
        "spots": result,
        "count": len(result)
    }


@mcp.tool(
    name='get_spots_by_city',
    description='根据城市名称获取景点数据（从本地JSON文件读取）'
)
def get_spots_by_city(province: str, city: str) -> Dict[str, Any]:
    target_path = os.path.join(DATA_ROOT, province, city)

    result = load_json_files_in_path(target_path)

    return {
        "province": province,
        "city": city,
        "spots": result,
        "count": len(result)
    }


@mcp.prompt(
    name='plan_trip',
    description='根据景点数据，生成旅游路径规划的提示词'
)
def plan_trip(message: str) -> str:
    return f"""你是一个专业的旅游规划助手。下面给你提供该省份/城市的景点 JSON 数据，请你根据景点评分、热度、是否免费、标签等信息规划最优旅游路线。

景点数据如下：
{message}

请给出：
1. 最佳旅游路线（包含顺序）
2. 每个景点推荐理由
3. 最适合游玩的时间段
4. 总体验优化建议
"""


@mcp.resource(
    uri="scenic://{province}/{city}",
    name='scenic_resource',
    description='资源协议：获取指定省份/城市的所有景点信息'
)
def scenic_resource(province: str, city: str):
    target_path = os.path.join(DATA_ROOT, province, city)
    result = load_json_files_in_path(target_path)
    
    return json.dumps({
        "province": province,
        "city": city,
        "spots": result
    }, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    mcp.run("sse")