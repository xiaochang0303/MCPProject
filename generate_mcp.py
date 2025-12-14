from mcp.server.fastmcp import FastMCP
import os
import requests
import uuid
from typing import Dict, Any

mcp = FastMCP("Image Generator")

# Nano Banana API Configuration
NANO_BANANA_API_URL = "https://api.acedata.cloud/nano-banana/images"


@mcp.prompt(
    name='travel_image_prompt_guide',
    description='旅游攻略长图的提示词生成框架 - 指导AI按四行格式生成图片描述'
)
def travel_image_prompt_guide(city: str, weather: str = "晴天 20度") -> str:
    """返回四行格式的图片 Prompt 生成框架"""
    return f"""请为「{city}」生成一张一日游攻略长图。

        ## 📋 四行格式框架（必须严格遵循）

        你需要按照以下**四行结构**生成图片的描述性 Prompt：

        **第一行**：背景说明
        - 描述：一张[城市]的一日游攻略长图，竖版海报，分为四个部分

        **第二行**：早晨景点画面
        - 时间：早晨 8:00-11:00
        - 内容：第一部分：早晨[景点名]的景色，[具体画面细节]

        **第三行**：中午景点画面  
        - 时间：中午 12:00-15:00
        - 内容：第二部分：中午[景点名]的景色，[具体画面细节]

        **第四行**：傍晚景点画面
        - 时间：傍晚 16:00-19:00
        - 内容：第三部分：傍晚[景点名]的景色，[具体画面细节]

        **第五行**：天气和风格
        - 天气：第四部分：天气图标显示「{weather}」，配上简单的穿衣建议图标
        - 风格：整体风格：[摄影风格/色彩/质感描述]

        ## 🎨 画面细节示例

        早晨场景示例：
        - "晨光洒在古建筑的飞檐上，石板路还带着露水，几只鸟儿在屋檐下栖息"
        - "清晨的湖面薄雾缭绕，渔船安静停泊，远处山峦若隐若现"

        中午场景示例：
        - "阳光下的街道色彩鲜艳，红灯笼高挂，游客在小吃摊前排队"
        - "正午的园林光影斑驳，荷花盛开，游人在凉亭中休憩拍照"

        傍晚场景示例：
        - "夕阳将整个塔身染成金色，晚霞映红天空，情侣在湖边漫步"
        - "黄昏时分的古镇灯火初上，石桥倒影在水中，天空呈现紫红渐变"

        风格描述示例：
        - "现代旅游海报风格，高清摄影质感，色彩明亮饱和，干净整洁的排版"
        - "电影级摄影，自然光影，真实细腻，色调温暖，富有故事感"

        ## ⚡ 执行步骤

        1. **获取景点**：使用 `get_spots_by_city` 工具获取{city}的景点数据
        2. **选择景点**：从中选择3个高评分景点（早/中/晚）
        3. **生成 Prompt**：按四行格式构建完整描述（每行都要详细！）
        4. **调用生成**：使用 `generate_image_nano_banana` 工具生成图片
        - prompt: 你生成的完整四行描述
        - width: 1024
        - height: 2048（长图比例）

        ## ✅ 检查清单

        生成 Prompt 前确保包含：
        - ✓ 明确说明"竖版海报，分为四个部分"
        - ✓ 三个景点的**具体名称**
        - ✓ 每个景点的**详细画面描述**（不少于15字）
        - ✓ 符合时间段的光线和氛围
        - ✓ 天气「{weather}」和穿衣建议
        - ✓ 明确的摄影风格说明

        ## ❌ 常见错误

        不要：
        - ❌ 省略任何一行
        - ❌ 只写景点名不写画面细节
        - ❌ 使用模糊词汇如"美丽的"、"好看的"
        - ❌ 忘记风格描述

        现在开始为{city}生成吧！
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
    token = "a0adca3025b447f39473d852043281fe"
    
    if not token:
        return {
            "success": False,
            "message": "错误: 未找到 API Token。"
        }
    
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
            
            # Check for image URL
            image_url = None
            
            if "image_urls" in result and result["image_urls"]:
                image_url = result["image_urls"][0]
            elif "data" in result and isinstance(result["data"], list) and len(result["data"]) > 0:
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
                        local_path = None
                except Exception as save_err:
                    print(f"Failed to save image: {save_err}")
                    local_path = None

            return {
                "success": True,
                "data": result,
                "trace_id": trace_id,
                "image_url": image_url,
                "local_path": local_path,
                "message": "图片生成成功" + (f"，已保存至 {local_path}" if local_path else "")
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
    import sys
    
    if "--sse" in sys.argv or os.getenv("MCP_TRANSPORT") == "sse":
        print("🚀 启动 Image Generator MCP 服务器 (SSE模式)")
        print("   服务名称: Image Generator")
        print("   工具数量: 2")
        print("   传输协议: Server-Sent Events (SSE)")
        mcp.run(transport="sse")
    else:
        mcp.run()