from mcp.server.fastmcp import FastMCP
import os
from typing import List, Dict, Any
import sys
import os
from tourmcp import get_spots_by_city
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

mcp = FastMCP("Xiaohongshu Publisher")


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
    基于省份、城市及景点信息，生成可直接发布到「小红书」的平台级笔记内容，
    自动融合【真实体验感 + 实用信息 + 情绪价值】，适用于旅游种草场景。

    ========================
    📥 参数说明
    ========================

    province : str
        省份名称，用于增强地域标签与搜索权重
        示例："浙江省"、"四川省"

    city : str
        城市名称，用于构建城市级旅游场景
        示例："杭州"、"成都"

    spot_name : Optional[str]
        指定的具体景点名称：
        - 若传入：生成「单一景点深度种草 / 打卡攻略」类内容
        - 若不传：生成「城市一日游 / 城市必去清单」类内容
        示例："西湖"、"宽窄巷子"、None

    style : str
        内容表现风格，影响文案语气、结构与重点：
        - "旅游攻略"：偏实用、时间线、路线、预算
        - "Vlog"：第一人称叙述，偏感受与氛围
        - "美食探店"：突出吃喝、排队、性价比
        - "打卡分享"：短句、强情绪、强推荐
        - "情侣旅行" / "亲子出游" / "周末逃离"（可扩展）
        
        默认建议使用："旅游攻略"

    ========================
    📤 返回内容结构
    ========================

    返回一个 Dict[str, Any]，包含以下字段：

    {
        "title": str,
            # 小红书风格标题（1～15字）
            # 含情绪词 / 数字 / 地点关键词，具备点击吸引力

        "content": str,
            # 正文内容（900~1500字）
            # 使用分段结构 + 表情符号
            # 包含：游玩顺序 / 体验感受 / 实用建议 / 避坑提示

        "highlights": List[str],
            # 3~5 条「一眼看懂」的亮点总结
            # 适合前端做卡片或加粗展示

        "tips": List[str],
            # 实用小贴士 / 避坑建议
            # 如：最佳时间、拍照点、人少路线、注意事项

        "budget": str,
            # 人均预算区间
            # 示例："人均 200–300 元"、"免费 + 餐饮约 100 元"

        "best_time": str,
            # 推荐游玩时间或季节
            # 示例："春秋最佳，避开节假日中午"

        "hashtags": List[str],
            # 推荐的小红书话题标签（10~15 个）
            # 包含城市名 / 景点名 / 场景词 / 情绪词
            # 示例：#杭州旅游 #周末去哪玩 #城市漫步

        "call_to_action": str
            # 行动引导语
            # 示例："记得收藏，下次来直接照着走！"
    }

    ========================
    🎯 内容生成原则
    ========================

    - 标题必须具备「种草感」，避免像说明书
    - 正文避免流水账，强调真实体验与情绪共鸣
    - 信息密度适中，适合手机阅读
    - 用词贴近真实用户，而非官方宣传语
    - 可适度使用 emoji，但不过度

    ========================
    🧩 使用示例
    ========================

    generate_xhs_note(
        province="四川省",
        city="成都",
        spot_name="宽窄巷子",
        style="打卡分享"
    )

    或：

    generate_xhs_note(
        province="浙江省",
        city="杭州",
        spot_name=None,
        style="旅游攻略"
    )
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
        title = f"🌟{city}必去景点清单！{len(top_spots)}个宝藏地一次玩透✨"

        content = f"📍【{city}旅游攻略】\n"
        content += f"这次整理了{len(top_spots)}个超值得打卡的地方，\n"
        content += f"适合第一次来{city}，直接照着玩不踩雷👇\n\n"

        total_budget = 0

        for i, spot in enumerate(top_spots, 1):
            ticket = spot.get("ticket_price", 0)
            budget = spot.get("budget", 50)
            total_budget += budget

            content += f"{i}️⃣ **{spot.get('name', '未知景点')}**\n"
            content += f"⭐️ 评分：{spot.get('rating', 'N/A')}\n"

            if spot.get("是否免费"):
                content += "💰 门票：免费\n"
            else:
                content += f"💰 门票：约 {ticket} 元\n"

            content += f"📸 亮点：{spot.get('highlight', '非常适合拍照和慢慢逛')}\n"
            content += f"🕒 建议游玩：{spot.get('duration', '1-2小时')}\n\n"

        content += "💡【游玩小贴士】\n"
        content += f"- 建议安排 {len(top_spots)} 天游玩，节奏更舒服\n"
        content += "- 尽量错峰出行，上午体验感最好\n"
        content += "- 穿一双好走路的鞋，很多地方需要步行\n\n"

        content += f"💰【人均预算】约 {total_budget} 元（不含住宿）\n"
        content += "👉 记得收藏，来之前翻出来照着走就行！\n\n"

        content += f"#去哪儿旅行 #{city}旅游 #旅游攻略 #城市漫步"

        topics = [
            f"#{city}旅游",
            "#旅游攻略",
            "#城市一日游",
            "#周末去哪儿",
            "#旅行不踩雷"
        ]

    elif style == "Vlog":
        title = f"🎬{city}旅行Vlog｜这趟真的被狠狠治愈了"

        content = f"📹【{city}旅行Vlog】\n\n"
        content += "这次一个人慢慢逛了这座城市，\n"
        content += "把最真实的感受都记录下来了👇\n\n"

        for spot in top_spots:
            content += f"📍 **{spot.get('name', '未知景点')}**\n"
            content += f"✨ 感受：{spot.get('highlight', '现场比照片好看')}\n\n"

        content += "🎧 建议戴着耳机看，沉浸感拉满\n"
        content += "如果你也想来这个城市走走，一定会喜欢～\n\n"
        content += "❤️ 点赞 + 收藏，下次旅行直接抄作业\n\n"

        content += f"#{city}vlog #旅行vlog #一个人的旅行 #慢生活"

        topics = [
            f"#{city}vlog",
            "#旅行vlog",
            "#城市探索",
            "#治愈系旅行"
        ]

    elif style == "打卡分享":
        title = f"✨{city}拍照打卡｜真的随手一拍都是大片！"

        content = f"📸【{city}打卡合集】\n\n"
        content += "这几个地方真的太好拍了，\n"
        content += "不用滤镜都很出片👇\n\n"

        for spot in top_spots:
            content += f"📍 **{spot.get('name', '未知景点')}**\n"
            content += f"📷 拍照点：{spot.get('photo_spot', '随便拍都好看')}\n\n"

        content += "👭 约上姐妹 / 对象一起去真的很合适\n"
        content += "记得收藏，周末直接安排！💛\n\n"

        content += f"#{city}打卡 #拍照圣地 #周末去哪儿 #旅行分享"

        topics = [
            f"#{city}打卡",
            "#拍照圣地",
            "#旅行分享",
            "#周末游"
        ]

    else:
        title = f"{city}旅行推荐｜这些地方真的值得一去"

        content = f"整理了{city}值得去的几个地方，分享给你～\n\n"

        topics = [f"#{city}", "#旅行推荐", "#生活方式"]

    return {
        "success": True,
        "title": title,
        "content": content,
        "topics": topics,
        "spots_included": [s.get("name") for s in top_spots],
        "style": style,
        "estimated_budget": total_budget if style == "旅游攻略" else None
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
    import sys
    
    if "--sse" in sys.argv or os.getenv("MCP_TRANSPORT") == "sse":
        print("🚀 启动 Xiaohongshu Publisher MCP 服务器 (SSE模式)")
        print("   服务名称: Xiaohongshu Publisher")
        print("   工具数量: 4")
        print("   传输协议: Server-Sent Events (SSE)")
        mcp.run(transport="sse")
    else:
        mcp.run()