from mcp.server.fastmcp import FastMCP
import os
import json
from typing import List, Dict, Any
import base64
from io import BytesIO
import requests
import uuid

mcp = FastMCP("Tour Guide")

# Nano Banana API Configuration
NANO_BANANA_API_URL = "https://api.acedata.cloud/nano-banana/images"

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
    schedule_hours: int = 0
) -> Dict[str, Any]:
    """
    发布视频笔记到小红书
    
    参数:
        file_path: 视频文件的绝对路径
        title: 笔记标题
        content: 笔记内容描述
        topics: 话题标签列表，如 ["#旅游", "#攻略"]
        schedule_hours: 
    
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


import os
from typing import List, Dict, Any
# 补充必要的导入（若项目中未引入）
try:
    from upload_xiaohongshu import publish_image_post, get_driver, xiaohongshu_login
except ImportError:
    publish_image_post = None
    get_driver = None
    xiaohongshu_login = None


@mcp.tool(
    name='publish_xiaohongshu_images',
    description='发布图文笔记到小红书（需要已登录的浏览器会话），标题自动校验≤20字'
)
def publish_xiaohongshu_images(
    file_path: str,
    title: str,
    content: str,
    topics: List[str] = None,
    schedule_hours: int = 0
) -> Dict[str, Any]:
    """
    发布图文笔记到小红书（严格遵守小红书标题≤20字规则）
    
    参数:
        file_path: 图片文件的绝对路径（支持多图，用英文逗号分隔，如"/a.jpg,/b.jpg"）
        title: 笔记标题（自动校验≤20字，超长会截断并提示）
        content: 笔记内容描述
        topics: 话题标签列表，如 ["#旅游", "#攻略"]（默认：["#旅游", "#风景", "#打卡"]）
        schedule_hours: 定时发布的小时数（默认24小时后，范围：0-72小时）
    
    返回:
        发布结果信息（含标题处理、文件校验、发布状态等细节）
    """
    # ========== 基础参数校验 ==========
    # 1. 标题长度校验与处理（核心优化）
    MAX_TITLE_LEN = 20
    title_origin = title.strip()
    title_processed = title_origin
    title_warning = ""
    
    if len(title_processed) > MAX_TITLE_LEN:
        # 截断超长标题（保留20字）
        title_processed = title_processed[:MAX_TITLE_LEN]
        title_warning = f"标题超长（原长度{len(title_origin)}），已自动截断为20字：{title_processed}"
    
    # 2. 话题标签默认值
    if topics is None:
        topics = ["#旅游", "#风景", "#打卡"]
    # 标准化话题格式（确保带#）
    topics = [t if t.startswith("#") else f"#{t}" for t in topics]
    
    # 3. 定时发布小时数范围校验
    if not (1 <= schedule_hours <= 72):
        return {
            "success": False,
            "message": f"定时发布小时数非法（需1-72小时），当前值：{schedule_hours}"
        }
    
    # 4. 多文件路径校验
    file_paths = [fp.strip() for fp in file_path.split(",") if fp.strip()]
    missing_files = [fp for fp in file_paths if not os.path.exists(fp)]
    if missing_files:
        return {
            "success": False,
            "message": f"以下文件不存在：{', '.join(missing_files)}",
            "details": {"valid_files": [fp for fp in file_paths if fp not in missing_files]}
        }

    # ========== 依赖校验 ==========
    try:
        from upload_xiaohongshu import publish_image_post, get_driver, xiaohongshu_login
    except ImportError as e:
        return {
            "success": False,
            "message": f"缺少小红书发布依赖：{str(e)}",
            "suggestion": "请安装selenium并确保upload_xiaohongshu.py文件存在"
        }

    # ========== 发布逻辑 ==========
    driver = None
    try:
        driver = get_driver()
        # 登录校验
        login_result = xiaohongshu_login(driver)
        # 若login有返回值（如登录失败），直接返回
        if login_result and not login_result.get("success", True):
            return {
                "success": False,
                "message": "小红书登录失败",
                "details": {"login_error": str(login_result)}
            }
        
        # 发布笔记（使用处理后的标题）
        publish_result = publish_image_post(
            driver=driver,
            file_path=file_path,  # 保持原格式传给底层函数
            title=title_processed,
            content=content,
            topics=topics,
            date_offset_hours=schedule_hours
        )

        # 构造返回结果
        result = {
            "success": True,
            "message": "图文笔记发布成功" + (f" | {title_warning}" if title_warning else ""),
            "details": {
                "title_origin": title_origin,
                "title_processed": title_processed,
                "title_length": len(title_processed),
                "file_paths": file_paths,
                "topics": topics,
                "schedule_hours": schedule_hours,
                "publish_result": publish_result  # 透传底层发布结果
            }
        }
        if title_warning:
            result["warning"] = title_warning
        return result

    except Exception as e:
        # 细化异常类型提示
        error_type = type(e).__name__
        return {
            "success": False,
            "message": f"发布失败（{error_type}）：{str(e)}",
            "details": {
                "title_origin": title_origin,
                "title_processed": title_processed,
                "file_paths": file_paths
            }
        }
    finally:
        # 确保浏览器驱动关闭
        if driver:
            try:
                driver.quit()
            except:
                pass

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



@mcp.prompt(
    name='travel_image_prompt_guide',
    description='旅游攻略长图的提示词生成框架，强制AI按固定五行结构生成图片描述（含预算信息）'
)
def travel_image_prompt_guide(city: str, weather: str = "晴天 20度") -> str:
    """
    返回固定五行结构的图片 Prompt 生成框架
    每一行对应海报中的一个明确模块，包含景点画面 + 预算信息
    """
    return f"""请为「{city}」生成一张一日游攻略长图。

## 📋 输出格式要求（必须严格遵循）

你**只能输出五行内容**，不得多写或少写。  
每一行对应海报中的一个模块，**必须按顺序生成**，不可合并、不可省略。  
**所有景点行必须包含明确的“预算信息（元/人）”。**

---

### **第一行｜背景说明**
内容要求：
- 描述一张【{city}】的一日游攻略**竖版长图海报**
- 明确说明画面被划分为 **五个部分**
- 五个部分依次为：**早晨 / 中午 / 傍晚 / 天气穿搭 / 预算汇总**
- 定位为 **旅游信息图 / 社交平台分享**
- 明确说明：**预算为人均预算**

---

### **第二行｜早晨景点画面与预算**
内容要求（必须全部包含）：
- **时间：8:00–11:00**
- 一个**具体景点名称**
- 符合早晨氛围的画面描述（不少于 15 个汉字）
- **景点门票预算：XX 元/人（如无门票请写 0 元）**
- **早晨交通 + 简易早餐预算：XX 元/人**

输出内容必须在同一行内完成，不得拆分。

---

### **第三行｜中午景点画面与预算**
内容要求（必须全部包含）：
- **时间：12:00–15:00**
- 一个**与早晨不同的具体景点**
- 符合中午氛围的画面描述（不少于 15 个汉字）
- **景点门票预算：XX 元/人**
- **午餐 + 周边小交通预算：XX 元/人**

---

### **第四行｜傍晚景点画面与预算**
内容要求（必须全部包含）：
- **时间：16:00–19:00**
- 第三个**不同的具体景点**
- 明确体现夕阳 / 黄昏 / 夜幕初上的画面特征（不少于 15 个汉字）
- **景点门票预算：XX 元/人**
- **傍晚交通预算：XX 元/人**

---

### **第五行｜天气、穿衣建议与总预算**
内容要求（必须全部包含）：
- 天气信息：显示「{weather}」
- 给出**简单、可执行的穿衣建议**
- **一日游总预算汇总：XX 元/人**
  - 总预算必须 = 早晨 + 中午 + 傍晚 所有门票 + 交通 + 餐饮之和
- 描述整体画面风格（摄影风格 + 色彩 + 质感），适合旅游海报与生图模型

---

## 🎨 画面与预算参考示例（理解用，不可照抄）

早晨示例：
> 8:00–11:00，早晨在城市老街漫步，晨光柔和，石板路微湿，行人不多；门票 0 元/人，交通 + 早餐预算 15 元/人

中午示例：
> 12:00–15:00，中午在美食街游览，街道热闹，小吃摊热气腾腾；门票 0 元/人，午餐 + 交通预算 80 元/人

傍晚示例：
> 16:00–19:00，傍晚登上城市地标，夕阳将建筑染成金色；门票 40 元/人，交通预算 25 元/人

---

## ❌ 严禁事项

- ❌ 省略任何一行
- ❌ 缺失任意一个预算字段
- ❌ 总预算与分项预算不一致
- ❌ 使用模糊描述替代具体金额

现在开始为【{city}】生成符合要求的五行旅游攻略 Prompt。
"""



@mcp.tool(
    name='generate_image_nano_banana',
    description='使用 Nano Banana API 生成图片，请根据travel_image_prompt_guide生成提示词'
)
def generate_image_nano_banana(
    prompt: str,
    negative_prompt: str = "",
    num_images: int = 1,
    width: int = 1024,
    height: int = 1024
) -> Dict[str, Any]:
    """
    使用 Nano Banana API 生成图片
    
    参数:
        prompt: 图片描述 prompt，请根据mcp工具travel_image_prompt_guide生成提示词'
        negative_prompt: 负向提示词
        num_images: 生成图片数量 (默认 1)
        width: 图片宽度 (默认 1024)
        height: 图片高度 (默认 1024)
    
    返回:
        API 响应结果，包含图片 URL 或任务信息
    """
    # token = os.getenv("NANO_BANANA_TOKEN") 
    # if not token:
    #     # 尝试兼容 ACEDATA_TOKEN
    #     token = os.getenv("ACEDATA_TOKEN")
    
    # if not token:
    #     return {
    #         "success": False,
    #         "message": "错误: 未找到 API Token。请设置环境变量 NANO_BANANA_TOKEN 或 ACEDATA_TOKEN。"
    #     }
    token = "a0adca3025b447f39473d852043281fe"
    headers = {
        "authorization": f"Bearer {token}",
        "accept": "application/json",
        "content-type": "application/json"
    }
    
    payload = {
        "action": "generate",
        "model": "nano-banana",
        "prompt": prompt,
        "width": width,
        "height": height
    }
    
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt
        
    try:
        response = requests.post(NANO_BANANA_API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            trace_id = result.get("trace_id")
            
            # Check for image URL and download if present
            local_path = None
            image_url = None
            
            if "image_urls" in result and result["image_urls"]:
                image_url = result["image_urls"][0]
            elif "data" in result and isinstance(result["data"], list) and len(result["data"]) > 0:
                # Handle possible data list format
                first_item = result["data"][0]
                if isinstance(first_item, dict):
                    image_url = first_item.get("image_url") or first_item.get("url")

            if image_url:
                try:
                    # Create directory if not exists
                    save_dir = os.path.join(os.getcwd(), "generated_images")
                    os.makedirs(save_dir, exist_ok=True)
                    
                    # Generate filename
                    filename = f"generated_{uuid.uuid4()}.png"
                    local_path = os.path.join(save_dir, filename)
                    
                    # Download image
                    img_resp = requests.get(image_url, stream=True)
                    if img_resp.status_code == 200:
                        with open(local_path, 'wb') as f:
                            for chunk in img_resp.iter_content(1024):
                                f.write(chunk)
                    else:
                        local_path = None  # Download failed
                except Exception as save_err:
                    print(f"Failed to save image: {save_err}")
                    local_path = None

            return {
                "success": True,
                "data": result,
                "trace_id": trace_id,
                "image_url": image_url,
                "local_path": local_path,
                "message": "图片生成成功" + (f"，已保存至 {local_path}" if local_path else "，但保存失败")
            }
        else:
            return {
                "success": False,
                "message": f"API请求失败: {response.status_code}",
                "error": response.text
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"请求异常: {str(e)}"
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

