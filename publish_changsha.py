#!/usr/bin/env python3
import os
import sys
import time
from upload_xiaohongshu import get_driver, xiaohongshu_login, publish_image_post

def main():
    # 文件路径llll
    image_path = "/Users/xiaocan/MCP_Project/generated_images/trip_vis_-1023213573775567509.png"
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"错误：图片文件不存在: {image_path}")
        return
    
    # 小红书内容
    title = "长沙旅游攻略｜3天2夜精华版"
    content = """🌟长沙旅游攻略｜3天2夜精华版✨

Day1：岳麓山+岳麓书院+橘子洲
Day2：湖南省博物馆+杜甫江阁
Day3：长沙世界之窗+美食街

🍜必吃：茶颜悦色、臭豆腐、小龙虾
🚇交通：地铁方便，下载"长沙地铁"APP
🎫门票：博物馆需预约，部分景点免费

#长沙旅游 #旅游攻略 #长沙美食 #周末游"""
    
    topics = ["#长沙旅游", "#旅游攻略", "#长沙美食", "#周末游"]
    
    print("开始发布小红书图文笔记...")
    print(f"标题: {title}")
    print(f"图片: {image_path}")
    
    try:
        # 获取浏览器驱动
        driver = get_driver()
        
        # 登录小红书
        xiaohongshu_login(driver)
        
        # 发布图文笔记
        publish_image_post(
            driver=driver,
            file_path=image_path,
            title=title,
            content=content,
            topics=topics,
            date_offset_hours=24
        )
        
        print("✅ 小红书图文笔记发布成功！")
        
    except Exception as e:
        print(f"❌ 发布失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()
