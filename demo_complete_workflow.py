"""
完整的旅游内容发布工作流演示
展示如何使用 MCP 工具从数据检索到内容生成再到发布
"""

from tourmcp import (
    get_spots_by_city,
    get_spots_by_cities,
    get_spots_statistics,
    visualize_city_ratings,
    visualize_spots_comparison,
    generate_xiaohongshu_content,
)
import json


def print_section(title):
    """打印章节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_json(data, indent=2):
    """美化打印JSON"""
    print(json.dumps(data, ensure_ascii=False, indent=indent))


def demo_data_retrieval():
    """演示数据检索功能"""
    print_section("1. 数据检索演示")
    
    # 单个城市
    print("📍 获取舟山市景点数据:")
    data = get_spots_by_city("浙江", "舟山")
    print(f"   找到 {data['count']} 个景点")
    if data['spots']:
        print(f"   第一个景点: {data['spots'][0].get('name', 'Unknown')}")
    
    # 多个城市
    print("\n📍 获取浙江省多个城市景点数据:")
    multi_data = get_spots_by_cities("浙江", ["杭州", "宁波", "舟山"])
    print(f"   共找到 {multi_data['count']} 个景点")
    print(f"   涉及城市: {', '.join(multi_data['cities'])}")


def demo_statistics():
    """演示统计分析功能"""
    print_section("2. 统计分析演示")
    
    # 城市统计
    print("📊 舟山市景点统计:")
    stats = get_spots_statistics("浙江", "舟山")
    if stats['success']:
        s = stats['statistics']
        print(f"   总景点数: {s['total_spots']}")
        print(f"   平均评分: {s['avg_rating']}")
        print(f"   评分分布:")
        for rating_range, count in s['rating_distribution'].items():
            print(f"      {rating_range}: {count} 个")
    
    # 省份统计
    print("\n📊 浙江省整体统计:")
    province_stats = get_spots_statistics("浙江")
    if province_stats['success']:
        s = province_stats['statistics']
        print(f"   总景点数: {s['total_spots']}")


def demo_visualization():
    """演示可视化功能"""
    print_section("3. 数据可视化演示")
    
    # 单城市评分可视化
    print("📈 生成舟山景点评分可视化数据:")
    viz_data = visualize_city_ratings("浙江", "舟山", output_format="data")
    if viz_data['success']:
        print(f"   类型: {viz_data['visualization_type']}")
        print(f"   景点数: {len(viz_data['data']['labels'])}")
        print(f"   景点: {', '.join(viz_data['data']['labels'][:3])}...")
    
    # 多城市对比
    print("\n📈 生成多城市对比数据:")
    comparison = visualize_spots_comparison(
        "浙江",
        ["杭州", "宁波", "舟山"],
        output_format="data"
    )
    if comparison['success']:
        print(f"   对比城市数: {len(comparison['data'])}")
        for city_info in comparison['data']:
            print(f"   {city_info['city']}: {city_info['count']} 个景点, "
                  f"平均 {city_info['avg_rating']} 分")


def demo_content_generation():
    """演示内容生成功能"""
    print_section("4. 小红书内容生成演示")
    
    styles = ["旅游攻略", "Vlog", "打卡分享"]
    
    for style in styles:
        print(f"\n✍️  生成{style}风格内容:")
        content = generate_xiaohongshu_content(
            province="浙江",
            city="舟山",
            style=style
        )
        
        if content['success']:
            print(f"   标题: {content['title']}")
            print(f"   内容预览: {content['content'][:80]}...")
            print(f"   话题标签: {', '.join(content['topics'])}")
            print(f"   包含景点: {', '.join(content['spots_included'])}")


def demo_complete_workflow():
    """演示完整的工作流程"""
    print_section("5. 完整工作流程演示")
    
    city = "杭州"
    province = "浙江"
    
    print(f"🎯 目标: 为 {city} 创建旅游推广内容\n")
    
    # 步骤 1: 获取数据
    print("步骤 1️⃣: 获取景点数据")
    spots_data = get_spots_by_city(province, city)
    print(f"   ✅ 找到 {spots_data['count']} 个景点")
    
    # 步骤 2: 分析数据
    print("\n步骤 2️⃣: 分析景点统计")
    stats = get_spots_statistics(province, city)
    if stats['success']:
        print(f"   ✅ 平均评分: {stats['statistics']['avg_rating']}")
        print(f"   ✅ 最高评分景点: {stats['statistics']['top_rated_spots'][0]['name'] if stats['statistics']['top_rated_spots'] else 'N/A'}")
    
    # 步骤 3: 生成内容
    print("\n步骤 3️⃣: 生成小红书内容")
    content = generate_xiaohongshu_content(province, city, style="旅游攻略")
    if content['success']:
        print(f"   ✅ 标题: {content['title']}")
        print(f"   ✅ 话题: {', '.join(content['topics'])}")
    
    # 步骤 4: 准备发布（说明）
    print("\n步骤 4️⃣: 准备发布")
    print("   📝 内容已生成，准备发布到小红书")
    print("   💡 使用命令:")
    print("      publish_xiaohongshu_images(")
    print(f"          file_path='/path/to/{city}_photo.jpg',")
    print(f"          title='{content['title']}',")
    print(f"          content='...',")
    print(f"          topics={content['topics']}")
    print("      )")
    
    print("\n✅ 完整工作流程演示完成！")


def main():
    """主函数"""
    print("\n" + "🎉" * 35)
    print("     旅游内容发布 MCP 工具 - 完整演示")
    print("🎉" * 35)
    
    try:
        # 运行各个演示
        demo_data_retrieval()
        demo_statistics()
        demo_visualization()
        demo_content_generation()
        demo_complete_workflow()
        
        # 总结
        print_section("📚 功能总结")
        print("✅ 数据检索: 支持单城市、多城市、省份级别查询")
        print("✅ 统计分析: 自动计算评分、分布等统计信息")
        print("✅ 数据可视化: 生成图表数据或Base64图片")
        print("✅ 内容生成: 多风格小红书内容自动生成")
        print("✅ 自动发布: 支持图文和视频笔记发布")
        print("✅ 批量处理: 支持多城市批量发布")
        
        print("\n" + "="*70)
        print("💡 提示:")
        print("   - 这些功能都已集成为 MCP 工具，可被 Claude Desktop 调用")
        print("   - 实际发布需要安装 selenium 并配置浏览器驱动")
        print("   - 首次使用需要登录小红书并保存 cookies")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
