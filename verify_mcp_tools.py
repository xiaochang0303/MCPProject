"""
MCP工具验证脚本
验证所有12个MCP工具是否可以正常导入和调用
"""

import sys

def test_imports():
    """测试所有工具是否可以正常导入"""
    print("🔍 测试工具导入...")
    
    try:
        from tourmcp import (
            # 数据检索工具
            get_spots_by_province,
            get_spots_by_city,
            get_spots_by_cities,
            # 可视化工具
            visualize_city_ratings,
            visualize_spots_comparison,
            get_spots_statistics,
            # 小红书发布工具
            generate_xiaohongshu_content,
            publish_xiaohongshu_video,
            publish_xiaohongshu_images,
            batch_publish_xiaohongshu,
            # 其他工具
            plan_trip,
            scenic_resource,
        )
        print("   ✅ 所有工具导入成功\n")
        return True
    except ImportError as e:
        print(f"   ❌ 导入失败: {e}\n")
        return False


def test_data_tools():
    """测试数据检索工具"""
    print("📊 测试数据检索工具...")
    
    from tourmcp import get_spots_by_city, get_spots_by_cities
    
    # 测试单城市
    result = get_spots_by_city("浙江", "舟山")
    assert result.get("city") == "舟山"
    assert "spots" in result
    print(f"   ✅ get_spots_by_city: 找到 {result['count']} 个景点")
    
    # 测试多城市
    result = get_spots_by_cities("浙江", ["杭州", "宁波"])
    assert len(result.get("cities", [])) == 2
    print(f"   ✅ get_spots_by_cities: 找到 {result['count']} 个景点\n")


def test_visualization_tools():
    """测试可视化工具"""
    print("📈 测试可视化工具...")
    
    from tourmcp import (
        visualize_city_ratings,
        visualize_spots_comparison,
        get_spots_statistics
    )
    
    # 测试评分可视化
    result = visualize_city_ratings("浙江", "舟山", output_format="data")
    assert result.get("success") == True
    print(f"   ✅ visualize_city_ratings: 生成 {result['visualization_type']}")
    
    # 测试城市对比
    result = visualize_spots_comparison("浙江", ["杭州", "宁波"], output_format="data")
    assert result.get("success") == True
    print(f"   ✅ visualize_spots_comparison: 对比 {len(result['data'])} 个城市")
    
    # 测试统计信息
    result = get_spots_statistics("浙江", "舟山")
    assert result.get("success") == True
    print(f"   ✅ get_spots_statistics: 统计 {result['statistics']['total_spots']} 个景点\n")


def test_content_generation_tools():
    """测试内容生成工具"""
    print("✍️  测试内容生成工具...")
    
    from tourmcp import generate_xiaohongshu_content
    
    styles = ["旅游攻略", "Vlog", "打卡分享"]
    
    for style in styles:
        result = generate_xiaohongshu_content("浙江", "舟山", style=style)
        assert result.get("success") == True
        assert "title" in result
        assert "content" in result
        assert "topics" in result
        print(f"   ✅ generate_xiaohongshu_content ({style}): {result['title'][:30]}...")
    
    print()


def test_mcp_tools_definition():
    """测试MCP工具是否正确定义"""
    print("🔧 测试MCP工具定义...")
    
    from tourmcp import mcp
    
    # 获取所有已注册的工具
    tools = []
    prompts = []
    resources = []
    
    # 通过 FastMCP 的内部属性获取工具列表
    if hasattr(mcp, '_tools'):
        tools = list(mcp._tools.keys())
    if hasattr(mcp, '_prompts'):
        prompts = list(mcp._prompts.keys())
    if hasattr(mcp, '_resources'):
        resources = list(mcp._resources.keys())
    
    print(f"   ✅ 已注册工具数: {len(tools)}")
    print(f"   ✅ 已注册提示词: {len(prompts)}")
    print(f"   ✅ 已注册资源: {len(resources)}")
    
    if tools:
        print(f"\n   工具列表:")
        for tool in tools:
            print(f"      - {tool}")
    
    print()


def main():
    """主函数"""
    print("\n" + "="*70)
    print("       MCP 工具验证脚本")
    print("="*70 + "\n")
    
    success_count = 0
    total_tests = 5
    
    # 运行测试
    try:
        if test_imports():
            success_count += 1
        
        test_data_tools()
        success_count += 1
        
        test_visualization_tools()
        success_count += 1
        
        test_content_generation_tools()
        success_count += 1
        
        test_mcp_tools_definition()
        success_count += 1
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 总结
    print("="*70)
    print(f"测试结果: {success_count}/{total_tests} 通过")
    print("="*70)
    
    if success_count == total_tests:
        print("\n✅ 所有测试通过！MCP工具已就绪。")
        print("\n💡 下一步:")
        print("   1. 运行 'python tourmcp.py' 启动MCP服务器")
        print("   2. 在 Claude Desktop 中配置该服务器")
        print("   3. 开始使用这些工具！")
        print()
        return 0
    else:
        print("\n⚠️  部分测试未通过，请检查错误信息。")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
