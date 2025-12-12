from tourmcp import generate_xiaohongshu_content
import json

def print_json(title, data):
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    print("测试小红书内容生成工具")
    
    # 测试 1: 生成旅游攻略风格内容
    print("\n测试 1: 生成舟山旅游攻略")
    result1 = generate_xiaohongshu_content(
        province="浙江",
        city="舟山",
        style="旅游攻略"
    )
    print_json("舟山旅游攻略", result1)
    
    # 测试 2: 生成Vlog风格内容
    print("\n测试 2: 生成杭州Vlog内容")
    result2 = generate_xiaohongshu_content(
        province="浙江",
        city="杭州",
        style="Vlog"
    )
    print_json("杭州Vlog", result2)
    
    # 测试 3: 生成打卡分享风格内容
    print("\n测试 3: 生成宁波打卡分享")
    result3 = generate_xiaohongshu_content(
        province="浙江",
        city="宁波",
        style="打卡分享"
    )
    print_json("宁波打卡分享", result3)
    
    # 测试 4: 指定景点生成内容
    print("\n测试 4: 生成普陀山景点内容")
    result4 = generate_xiaohongshu_content(
        province="浙江",
        city="舟山",
        spot_name="普陀山",
        style="旅游攻略"
    )
    print_json("普陀山景点内容", result4)
    
    print("\n" + "="*60)
    print("✅ 内容生成测试完成！")
    print("="*60)
    print("\n💡 提示: 要测试实际发布功能，需要:")
    print("   1. 安装 selenium: pip install selenium")
    print("   2. 配置浏览器驱动（Chrome/Firefox）")
    print("   3. 首次使用需要登录小红书并保存cookies")
    print("   4. 准备好要发布的图片或视频文件")
    print("\n示例发布命令:")
    print('   publish_xiaohongshu_images(')
    print('       file_path="/path/to/image.jpg",')
    print('       title="标题",')
    print('       content="内容",')
    print('       topics=["#旅游", "#攻略"]')
    print('   )')


if __name__ == "__main__":
    main()
