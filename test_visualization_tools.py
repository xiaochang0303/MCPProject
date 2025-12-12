from tourmcp import (
    visualize_city_ratings,
    visualize_spots_comparison,
    get_spots_statistics
)
import json

def print_json(title, data):
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    print("测试 MCP 可视化工具")
    
    # 测试 1: 获取单个城市评分数据
    print("\n测试 1: 获取舟山景点评分数据")
    result1 = visualize_city_ratings("浙江", "舟山", output_format="data")
    print_json("舟山景点评分数据", result1)
    
    # 测试 2: 对比多个城市
    print("\n测试 2: 对比浙江省多个城市")
    result2 = visualize_spots_comparison(
        "浙江",
        ["杭州", "宁波", "舟山"],
        output_format="data"
    )
    print_json("城市对比数据", result2)
    
    # 测试 3: 获取统计信息
    print("\n测试 3: 获取舟山景点统计信息")
    result3 = get_spots_statistics("浙江", "舟山")
    print_json("舟山景点统计", result3)
    
    # 测试 4: 获取省份统计信息
    print("\n测试 4: 获取浙江省整体统计信息")
    result4 = get_spots_statistics("浙江")
    print_json("浙江省景点统计", result4)
    
    # 如果 matplotlib 可用，测试图片生成
    try:
        import matplotlib
        print("\n测试 5: 生成图片（Base64编码）")
        result5 = visualize_city_ratings("浙江", "舟山", output_format="image")
        if result5.get("success"):
            print(f"✅ 成功生成图片，Base64长度: {len(result5.get('image_base64', ''))} 字符")
            print(f"   图片格式: {result5.get('format')}")
        else:
            print(f"❌ 图片生成失败: {result5.get('message')}")
    except ImportError:
        print("\n⚠️  matplotlib 未安装，跳过图片生成测试")


if __name__ == "__main__":
    main()
