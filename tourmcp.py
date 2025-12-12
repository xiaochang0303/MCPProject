from mcp.server.fastmcp import FastMCP
import os
import json
from typing import List, Dict, Any
import base64
from io import BytesIO

mcp = FastMCP("Tour Guide")

DATA_ROOT = "./data"   # 你的 JSON 数据根目录，例如：./data/浙江/舟山/朱家尖大青山景区/scene_info.json

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


# ==================== 小红书发布工具 ====================

@mcp.tool(
    name='publish_xiaohongshu_video',
    description='发布视频笔记到小红书（需要已登录的浏览器会话）'
)
def publish_xiaohongshu_video(
    file_path: str,
    title: str,
    content: str,
    topics: List[str] = None,
    schedule_hours: int = 24
) -> Dict[str, Any]:
    """
    发布视频笔记到小红书
    
    参数:
        file_path: 视频文件的绝对路径
        title: 笔记标题
        content: 笔记内容描述
        topics: 话题标签列表，如 ["#旅游", "#攻略"]
        schedule_hours: 定时发布的小时数（默认24小时后）
    
    返回:
        发布结果信息
    """
    try:
        # Import locally to avoid requiring selenium if not used
        from upload_xiaohongshu import publish_single_post, get_driver, xiaohongshu_login
        
        if topics is None:
            topics = ["#旅游", "#攻略", "#景点推荐"]
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "message": f"文件不存在: {file_path}"
            }
        
        driver = get_driver()
        try:
            xiaohongshu_login(driver)
            publish_single_post(
                driver=driver,
                file_path=file_path,
                title=title,
                content=content,
                topics=topics,
                date_offset_hours=schedule_hours
            )
            
            return {
                "success": True,
                "message": "视频笔记发布成功",
                "details": {
                    "file_path": file_path,
                    "title": title,
                    "topics": topics,
                    "schedule_hours": schedule_hours
                }
            }
        finally:
            driver.quit()
            
    except ImportError as e:
        return {
            "success": False,
            "message": f"缺少依赖: {str(e)}，请确保已安装 selenium"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"发布失败: {str(e)}"
        }


@mcp.tool(
    name='publish_xiaohongshu_images',
    description='发布图文笔记到小红书（需要已登录的浏览器会话）'
)
def publish_xiaohongshu_images(
    file_path: str,
    title: str,
    content: str,
    topics: List[str] = None,
    schedule_hours: int = 24
) -> Dict[str, Any]:
    """
    发布图文笔记到小红书
    
    参数:
        file_path: 图片文件的绝对路径（支持多图，用逗号分隔）
        title: 笔记标题
        content: 笔记内容描述
        topics: 话题标签列表，如 ["#旅游", "#攻略"]
        schedule_hours: 定时发布的小时数（默认24小时后）
    
    返回:
        发布结果信息
    """
    try:
        from upload_xiaohongshu import publish_image_post, get_driver, xiaohongshu_login
        
        if topics is None:
            topics = ["#旅游", "#风景", "#打卡"]
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "message": f"文件不存在: {file_path}"
            }
        
        driver = get_driver()
        try:
            xiaohongshu_login(driver)
            publish_image_post(
                driver=driver,
                file_path=file_path,
                title=title,
                content=content,
                topics=topics,
                date_offset_hours=schedule_hours
            )
            
            return {
                "success": True,
                "message": "图文笔记发布成功",
                "details": {
                    "file_path": file_path,
                    "title": title,
                    "topics": topics,
                    "schedule_hours": schedule_hours
                }
            }
        finally:
            driver.quit()
            
    except ImportError as e:
        return {
            "success": False,
            "message": f"缺少依赖: {str(e)}，请确保已安装 selenium"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"发布失败: {str(e)}"
        }


@mcp.tool(
    name='generate_xiaohongshu_content',
    description='根据景点信息生成小红书笔记内容'
)
def generate_xiaohongshu_content(
    province: str,
    city: str,
    spot_name: str = None,
    style: str = "旅游攻略"
) -> Dict[str, Any]:
    """
    根据景点信息生成小红书笔记内容
    
    参数:
        province: 省份名称
        city: 城市名称
        spot_name: 特定景点名称（可选，如果不指定则生成城市概览）
        style: 内容风格，如 "旅游攻略", "Vlog", "美食探店", "打卡分享"
    
    返回:
        生成的标题、内容和推荐话题
    """
    data = get_spots_by_city(province, city)
    spots = data.get("spots", [])
    
    if not spots:
        return {
            "success": False,
            "message": f"未找到 {city}, {province} 的景点数据"
        }
    
    # 如果指定了景点名称，只使用该景点
    if spot_name:
        spots = [s for s in spots if spot_name in s.get("name", "")]
        if not spots:
            return {
                "success": False,
                "message": f"未找到景点: {spot_name}"
            }
    
    # 选择评分最高的景点
    top_spots = sorted(
        spots,
        key=lambda x: float(x.get("rating", 0)),
        reverse=True
    )[:3]
    
    # 生成内容
    if style == "旅游攻略":
        title = f"🌟{city}必去景点！{len(top_spots)}个宝藏打卡地分享✨"
        content = f"📍{city}旅游攻略来啦！\n\n"
        
        for i, spot in enumerate(top_spots, 1):
            content += f"{i}️⃣ {spot.get('name', '未知景点')}\n"
            content += f"⭐️ 评分: {spot.get('rating', 'N/A')}\n"
            if spot.get('是否免费'):
                content += "💰 免费景点！\n"
            content += "\n"
        
        content += f"💡小贴士：建议游玩{len(top_spots)}天，慢慢感受{city}的魅力~\n"
        content += f"\n#去哪儿旅行 #{city}旅游 #旅游攻略"
        
        topics = [f"#{city}旅游", "#旅游攻略", "#景点推荐", "#打卡"]
        
    elif style == "Vlog":
        title = f"🎬{city}Vlog | 探索{len(top_spots)}个绝美景点！"
        content = f"📹今天带大家逛{city}！\n\n"
        content += f"这次打卡了{len(top_spots)}个超美的地方：\n\n"
        
        for i, spot in enumerate(top_spots, 1):
            content += f"📍{spot.get('name', '未知景点')}\n"
        
        content += f"\n每一个都超级出片！\n"
        content += f"喜欢的宝子们记得点赞收藏哦~\n"
        content += f"\n#{city}vlog #旅行vlog #城市探索"
        
        topics = [f"#{city}vlog", "#旅行vlog", "#vlog日常", "#探店"]
        
    elif style == "打卡分享":
        title = f"✨{city}打卡|这些地方真的太美了！"
        content = f"📸{city}打卡合集来咯~\n\n"
        
        for spot in top_spots:
            content += f"📍{spot.get('name', '未知景点')}\n"
        
        content += f"\n随手一拍都是大片！\n"
        content += f"姐妹们赶紧安排起来💕\n"
        content += f"\n#{city}打卡 #旅行分享 #周末去哪儿"
        
        topics = [f"#{city}打卡", "#打卡", "#旅行分享", "#周末游"]
    
    else:
        title = f"{city}旅游 | {top_spots[0].get('name', '景点')}超值得！"
        content = f"推荐{city}的{len(top_spots)}个好地方！\n\n"
        topics = [f"#{city}", "#旅游", "#推荐"]
    
    return {
        "success": True,
        "title": title,
        "content": content,
        "topics": topics,
        "spots_included": [s.get("name") for s in top_spots],
        "style": style
    }


@mcp.tool(
    name='batch_publish_xiaohongshu',
    description='批量发布小红书笔记（支持多个城市的景点内容）'
)
def batch_publish_xiaohongshu(
    province: str,
    cities: List[str],
    file_paths: List[str],
    style: str = "旅游攻略",
    schedule_interval_hours: int = 24
) -> Dict[str, Any]:
    """
    批量生成并发布小红书笔记
    
    参数:
        province: 省份名称
        cities: 城市列表
        file_paths: 对应每个城市的媒体文件路径列表
        style: 内容风格
        schedule_interval_hours: 每篇笔记之间的发布间隔（小时）
    
    返回:
        批量发布结果
    """
    if len(cities) != len(file_paths):
        return {
            "success": False,
            "message": "城市数量与文件数量不匹配"
        }
    
    results = []
    
    for i, (city, file_path) in enumerate(zip(cities, file_paths)):
        # 生成内容
        content_result = generate_xiaohongshu_content(province, city, style=style)
        
        if not content_result.get("success"):
            results.append({
                "city": city,
                "success": False,
                "message": content_result.get("message")
            })
            continue
        
        # 计算发布时间
        schedule_hours = schedule_interval_hours * (i + 1)
        
        # 判断文件类型
        is_video = file_path.lower().endswith(('.mp4', '.mov', '.avi'))
        
        # 发布
        if is_video:
            publish_result = publish_xiaohongshu_video(
                file_path=file_path,
                title=content_result["title"],
                content=content_result["content"],
                topics=content_result["topics"],
                schedule_hours=schedule_hours
            )
        else:
            publish_result = publish_xiaohongshu_images(
                file_path=file_path,
                title=content_result["title"],
                content=content_result["content"],
                topics=content_result["topics"],
                schedule_hours=schedule_hours
            )
        
        results.append({
            "city": city,
            "success": publish_result.get("success"),
            "title": content_result["title"],
            "schedule_hours": schedule_hours,
            "message": publish_result.get("message")
        })
    
    success_count = sum(1 for r in results if r.get("success"))
    
    return {
        "success": True,
        "total": len(results),
        "success_count": success_count,
        "failed_count": len(results) - success_count,
        "results": results
    }

if __name__ == "__main__":
    # 运行 MCP 服务器
    # 默认使用 stdio 模式，可以通过环境变量切换到 SSE 模式
    import sys
    
    # 检查是否指定了 SSE 模式
    if "--sse" in sys.argv or os.getenv("MCP_TRANSPORT") == "sse":
        # SSE 模式配置
        print("🚀 启动 MCP 服务器 (SSE模式)")
        print("   传输协议: Server-Sent Events (SSE)")
        print("   工具数量: 12")
        print("\n💡 Claude Desktop 配置示例:")
        print('   {"url": "http://localhost:8000/sse"}')
        print("\n注意: FastMCP 的 SSE 模式端口由框架内部管理")
        print("如需自定义端口，请参考 FastMCP 文档")
        print()
        
        mcp.run(transport="sse")
    else:
        # 默认 stdio 模式
        mcp.run()