from mcp.server.fastmcp import FastMCP
import os
import json
from typing import List, Dict, Any
import base64
from io import BytesIO

mcp = FastMCP("Tour Guide")

DATA_ROOT = "./data"   # 你的 JSON 数据根目录

# Try to import matplotlib for visualization
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    # Set Chinese font for matplotlib
    try:
        matplotlib.rcParams['font.family'] = ['Heiti TC']
    except:
        try:
            matplotlib.rcParams['font.family'] = ['SimHei', 'Arial Unicode MS']
        except:
            pass
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


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


@mcp.tool(
    name='get_spots_by_cities',
    description='根据省份和城市列表获取多个城市的景点数据'
)
def get_spots_by_cities(province: str, cities: List[str]) -> Dict[str, Any]:
    all_spots = []
    total_count = 0
    
    for city in cities:
        target_path = os.path.join(DATA_ROOT, province, city)
        city_spots = load_json_files_in_path(target_path)
        # Add city info to spots for context
        for spot in city_spots:
            spot['city'] = city
        all_spots.extend(city_spots)
        total_count += len(city_spots)

    return {
        "province": province,
        "cities": cities,
        "spots": all_spots,
        "count": total_count
    }


@mcp.prompt(
    name='plan_trip',
    description='根据景点数据，生成旅游路径规划的提示词'
)
def plan_trip(message: str) -> str:
    return f"""你是一个专业的旅游规划助手。下面给你提供旅游目的地的景点 JSON 数据，请你根据景点评分、热度、地理位置等信息规划最优旅游路线。

景点数据如下：
{message}

请给出：
1. 最佳旅游路线（包含天数和每日顺序，如果是多城市，请合理安排城市间流转）
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


@mcp.tool(
    name='visualize_city_ratings',
    description='生成城市景点评分的可视化数据（返回Base64编码的图片或数据）'
)
def visualize_city_ratings(province: str, city: str, output_format: str = "data") -> Dict[str, Any]:
    """
    生成城市景点评分可视化
    output_format: "data" 返回数据, "image" 返回base64编码的图片
    """
    data = get_spots_by_city(province, city)
    spots = data.get("spots", [])
    
    if not spots:
        return {
            "success": False,
            "message": f"未找到 {city}, {province} 的景点数据"
        }
    
    spot_names = [spot.get("name", "Unknown") for spot in spots]
    spot_ratings = [float(spot.get("rating", 0)) for spot in spots]
    
    if output_format == "data":
        return {
            "success": True,
            "province": province,
            "city": city,
            "visualization_type": "ratings_bar_chart",
            "data": {
                "labels": spot_names,
                "values": spot_ratings
            }
        }
    
    elif output_format == "image" and MATPLOTLIB_AVAILABLE:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(spot_names, spot_ratings, color='skyblue')
        ax.set_xlabel('景点名称')
        ax.set_ylabel('评分')
        ax.set_title(f'{city}, {province} 景点评分')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save to BytesIO and encode as base64
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return {
            "success": True,
            "province": province,
            "city": city,
            "visualization_type": "ratings_bar_chart",
            "image_base64": img_base64,
            "format": "png"
        }
    
    else:
        return {
            "success": False,
            "message": "matplotlib 未安装，无法生成图片，请使用 output_format='data'"
        }


@mcp.tool(
    name='visualize_spots_comparison',
    description='生成多个城市景点数量和平均评分的对比可视化'
)
def visualize_spots_comparison(province: str, cities: List[str], output_format: str = "data") -> Dict[str, Any]:
    """
    生成多城市景点对比可视化
    output_format: "data" 返回数据, "image" 返回base64编码的图片
    """
    city_data = []
    
    for city in cities:
        data = get_spots_by_city(province, city)
        spots = data.get("spots", [])
        if spots:
            avg_rating = sum(float(s.get("rating", 0)) for s in spots) / len(spots)
            city_data.append({
                "city": city,
                "count": len(spots),
                "avg_rating": round(avg_rating, 2)
            })
    
    if not city_data:
        return {
            "success": False,
            "message": f"未找到 {province} 中任何城市的景点数据"
        }
    
    if output_format == "data":
        return {
            "success": True,
            "province": province,
            "visualization_type": "city_comparison",
            "data": city_data
        }
    
    elif output_format == "image" and MATPLOTLIB_AVAILABLE:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        cities_list = [d["city"] for d in city_data]
        counts = [d["count"] for d in city_data]
        ratings = [d["avg_rating"] for d in city_data]
        
        # 景点数量对比
        ax1.bar(cities_list, counts, color='lightcoral')
        ax1.set_xlabel('城市')
        ax1.set_ylabel('景点数量')
        ax1.set_title(f'{province} 各城市景点数量对比')
        ax1.tick_params(axis='x', rotation=45)
        
        # 平均评分对比
        ax2.bar(cities_list, ratings, color='lightgreen')
        ax2.set_xlabel('城市')
        ax2.set_ylabel('平均评分')
        ax2.set_title(f'{province} 各城市平均评分对比')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return {
            "success": True,
            "province": province,
            "visualization_type": "city_comparison",
            "image_base64": img_base64,
            "format": "png"
        }
    
    else:
        return {
            "success": False,
            "message": "matplotlib 未安装，无法生成图片，请使用 output_format='data'"
        }


@mcp.tool(
    name='get_spots_statistics',
    description='获取指定城市或省份的景点统计信息'
)
def get_spots_statistics(province: str, city: str = None) -> Dict[str, Any]:
    """
    获取景点统计信息，包括总数、平均评分、评分分布等
    """
    if city:
        data = get_spots_by_city(province, city)
        location = f"{city}, {province}"
    else:
        data = get_spots_by_province(province)
        location = province
    
    spots = data.get("spots", [])
    
    if not spots:
        return {
            "success": False,
            "message": f"未找到 {location} 的景点数据"
        }
    
    ratings = [float(s.get("rating", 0)) for s in spots if s.get("rating")]
    
    # 评分分布统计
    rating_distribution = {
        "5.0": 0,
        "4.0-4.9": 0,
        "3.0-3.9": 0,
        "2.0-2.9": 0,
        "< 2.0": 0
    }
    
    for rating in ratings:
        if rating >= 5.0:
            rating_distribution["5.0"] += 1
        elif rating >= 4.0:
            rating_distribution["4.0-4.9"] += 1
        elif rating >= 3.0:
            rating_distribution["3.0-3.9"] += 1
        elif rating >= 2.0:
            rating_distribution["2.0-2.9"] += 1
        else:
            rating_distribution["< 2.0"] += 1
    
    return {
        "success": True,
        "location": location,
        "statistics": {
            "total_spots": len(spots),
            "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0,
            "max_rating": max(ratings) if ratings else 0,
            "min_rating": min(ratings) if ratings else 0,
            "rating_distribution": rating_distribution,
            "top_rated_spots": sorted(
                [{"name": s.get("name"), "rating": s.get("rating")} for s in spots if s.get("rating")],
                key=lambda x: float(x["rating"]),
                reverse=True
            )[:5]
        }
    }


if __name__ == "__main__":
    # 运行 MCP 服务器
    import sys
    
    if "--sse" in sys.argv or os.getenv("MCP_TRANSPORT") == "sse":
        print("🚀 启动 Tour Guide MCP 服务器 (SSE模式)")
        print("   服务名称: Tour Guide")
        print("   工具数量: 6")
        print("   传输协议: Server-Sent Events (SSE)")
        mcp.run(transport="sse")
    else:
        mcp.run()