#!/usr/bin/env python3
"""
旅游规划MCP服务独立测试脚本
无需启动完整的MCP服务器，直接测试各个功能
"""

import sys
import os
import json
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 创建模拟的MCP环境
class MockMCP:
    """模拟MCP环境，用于独立测试"""
    
    def __init__(self):
        self.tools = {}
        self.resources = {}
        self.prompts = {}
    
    def tool(self, name=None, description=None):
        def decorator(func):
            self.tools[name or func.__name__] = {
                'function': func,
                'description': description
            }
            return func
        return decorator
    
    def resource(self, uri=None, name=None, description=None):
        def decorator(func):
            self.resources[name or func.__name__] = {
                'function': func,
                'uri': uri,
                'description': description
            }
            return func
        return decorator
    
    def prompt(self, name=None, description=None):
        def decorator(func):
            self.prompts[name or func.__name__] = {
                'function': func,
                'description': description
            }
            return func
        return decorator

# 导入主模块并修改MCP装饰器
import MCPProject.tourmcp as mcp_module

# 创建模拟MCP实例
mock_mcp = MockMCP()

# 重新应用装饰器
mcp_module.mcp = type('MockFastMCP', (), {
    'tool': mock_mcp.tool,
    'resource': mock_mcp.resource,
    'prompt': mock_mcp.prompt
})()

# 重新导入模块以重新注册所有功能
import importlib
importlib.reload(mcp_module)

print("🚀 旅游规划MCP服务独立测试工具")
print("=" * 50)

def test_get_weather():
    """测试天气查询功能"""
    print("\n1. 测试天气查询功能")
    print("-" * 30)
    
    # 测试实时天气
    result = mcp_module.get_weather("北京", "base")
    print(f"北京实时天气: {json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, dict) else result}")
    
    # 测试天气预报
    result = mcp_module.get_weather("上海", "all")
    print(f"\n上海天气预报: {json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, dict) else result}")

def test_get_geocode():
    """测试地理编码功能"""
    print("\n2. 测试地理编码功能")
    print("-" * 30)
    
    result = mcp_module.get_geocode("北京市天安门广场")
    print(f"天安门地理编码: {json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, dict) else result}")
    
    result = mcp_module.get_geocode("东方明珠", "上海")
    print(f"\n东方明珠地理编码: {json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, dict) else result}")

def test_route_planning():
    """测试路径规划功能"""
    print("\n3. 测试路径规划功能")
    print("-" * 30)
    
    result = mcp_module.route_planning("天安门", "故宫", "北京")
    print(f"天安门到故宫路径规划:")
    if result.get("success"):
        routes = result.get("routes", {})
        for mode, info in routes.items():
            print(f"  {mode}: {info.get('distance_km', 0)}公里, {info.get('duration_min', 0)}分钟")
        recommendation = result.get("recommendation", {}).get("best_option", {})
        print(f"  推荐: {recommendation.get('method')}, 理由: {recommendation.get('reason')}")
    else:
        print(f"  错误: {result.get('message')}")

def test_search_nearby():
    """测试附近搜索功能"""
    print("\n4. 测试附近搜索功能")
    print("-" * 30)
    
    result = mcp_module.search_nearby("故宫", "餐厅", 1000, "北京")
    print(f"故宫附近餐厅搜索:")
    if result.get("success"):
        pois = result.get("pois", [])
        print(f"  找到 {len(pois)} 个结果:")
        for poi in pois[:5]:  # 只显示前5个
            print(f"  - {poi.get('name')} ({poi.get('type')})")
    else:
        print(f"  错误: {result.get('message')}")

def test_get_spots_by_city():
    """测试城市景点查询"""
    print("\n5. 测试城市景点查询")
    print("-" * 30)
    
    # 首先确保有测试数据
    data_dir = Path("./data")
    if data_dir.exists():
        provinces = [d for d in data_dir.iterdir() if d.is_dir()]
        if provinces:
            province = provinces[0].name
            province_path = data_dir / province
            cities = [d.name for d in province_path.iterdir() if d.is_dir()]
            if cities:
                city = cities[0]
                result = mcp_module.get_spots_by_city(province, city, include_weather=True)
                print(f"{province} {city} 景点查询:")
                print(f"  找到 {result.get('count', 0)} 个景点")
                if result.get("weather"):
                    weather = result.get("weather", {})
                    print(f"  天气: {weather.get('weather')}, 温度: {weather.get('temperature')}°C")
                return
    
    print("  警告: 未找到测试数据，请先创建 ./data/省份/城市/ 目录结构")
    # 测试默认数据
    result = mcp_module.get_spots_by_city("北京", "北京", include_weather=False)
    print(f"北京景点查询: 找到 {result.get('count', 0)} 个景点")

def test_plan_trip_with_routing():
    """测试智能旅游规划"""
    print("\n6. 测试智能旅游规划")
    print("-" * 30)
    
    result = mcp_module.plan_trip_with_routing("北京", "北京", 2)
    if result.get("success"):
        print(f"北京2日游规划:")
        cost = result.get("cost_estimation", {})
        print(f"  总花费: {cost.get('total_yuan', 0)}元")
        print(f"  交通: {cost.get('transportation_yuan', 0)}元")
        print(f"  餐饮: {cost.get('food_yuan', 0)}元")
        print(f"  住宿: {cost.get('accommodation_yuan', 0)}元")
        
        daily_plans = result.get("daily_plans", [])
        for day_plan in daily_plans:
            print(f"\n  第{day_plan.get('day')}天:")
            for spot in day_plan.get("spots", []):
                print(f"    - {spot.get('name')}")
    else:
        print(f"  错误: {result.get('message')}")

def test_search_spots_near_location():
    """测试附近景点搜索"""
    print("\n7. 测试附近景点搜索")
    print("-" * 30)
    
    result = mcp_module.search_spots_near_location("王府井", 2, 4.0)
    if result.get("success"):
        print(f"王府井附近景点:")
        spots = result.get("spots", [])
        print(f"  匹配到 {len(spots)} 个景点:")
        for spot in spots[:5]:
            print(f"  - {spot.get('name')} (评分: {spot.get('rating')}, 距离: {spot.get('distance_km')}km)")
    else:
        print(f"  错误: {result.get('message')}")

def test_get_travel_time_estimation():
    """测试旅行时间估算"""
    print("\n8. 测试旅行时间估算")
    print("-" * 30)
    
    spots = ["天安门", "故宫", "颐和园"]
    result = mcp_module.get_travel_time_estimation(spots, "北京酒店")
    if result.get("success"):
        print(f"景点游览时间估算:")
        print(f"  景点数量: {result.get('spots_count')}")
        print(f"  总时间: {result.get('estimated_hours')}小时")
        print(f"  旅行时间: {result.get('total_travel_time_min')}分钟")
        print(f"  游览时间: {result.get('total_visit_time_min')}分钟")
        print(f"  总花费: {result.get('total_cost_yuan')}元")
    else:
        print(f"  错误: {result.get('message')}")

def test_generate_static_map():
    """测试静态地图生成"""
    print("\n9. 测试静态地图生成")
    print("-" * 30)
    
    result = mcp_module.generate_static_map("天安门", 15, "400 * 300")
    if result.get("success"):
        print(f"静态地图生成成功:")
        print(f"  位置: {result.get('location')}")
        print(f"  缩放: {result.get('zoom')}")
        print(f"  大小: {result.get('size')}")
        print(f"  Base64图片长度: {len(result.get('image_base64', ''))} 字符")
        
        # 可以选择保存图片
        save = input("是否保存地图图片? (y/n): ")
        if save.lower() == 'y':
            with open("map.png", "wb") as f:
                import base64
                f.write(base64.b64decode(result["image_base64"]))
            print("  图片已保存为 map.png")
    else:
        print(f"  错误: {result.get('message')}")

def test_intelligent_trip_plan():
    """测试智能旅游规划提示"""
    print("\n10. 测试智能旅游规划提示")
    print("-" * 30)
    
    prompt = mcp_module.intelligent_trip_plan("北京", 3, 2000)
    print("生成的提示词模板:")
    print("-" * 40)
    print(prompt)
    print("-" * 40)
    print("\n您可以将此提示词提供给AI助手，它会生成详细的旅游计划")

def test_all_amap_apis():
    """测试高德地图所有API功能"""
    print("\n🔄 测试高德地图所有API功能")
    print("=" * 50)
    
    # 根据您提供的图片，测试所有API功能
    apis_to_test = [
        ("基础API - 地理/逆地理编码", test_get_geocode),
        ("基础API - 路径规划", test_route_planning),
        ("基础API - 静态地图", test_generate_static_map),
        ("高级API - 天气查询", test_get_weather),
        ("高级API - 搜索POI", test_search_nearby),
    ]
    
    for api_name, test_func in apis_to_test:
        print(f"\n🔧 测试 {api_name}")
        print("-" * 40)
        try:
            test_func()
        except Exception as e:
            print(f"  测试失败: {str(e)}")

def interactive_test():
    """交互式测试菜单"""
    while True:
        print("\n" + "=" * 50)
        print("📱 旅游规划MCP服务测试菜单")
        print("=" * 50)
        print("1. 测试天气查询")
        print("2. 测试地理编码")
        print("3. 测试路径规划")
        print("4. 测试附近搜索")
        print("5. 测试城市景点")
        print("6. 测试智能规划")
        print("7. 测试附近景点")
        print("8. 测试时间估算")
        print("9. 测试静态地图")
        print("10. 测试提示模板")
        print("11. 测试所有高德API")
        print("12. 运行完整测试")
        print("0. 退出")
        
        choice = input("\n请选择测试项目 (0-12): ").strip()
        
        if choice == "0":
            print("👋 退出测试")
            break
        elif choice == "1":
            test_get_weather()
        elif choice == "2":
            test_get_geocode()
        elif choice == "3":
            test_route_planning()
        elif choice == "4":
            test_search_nearby()
        elif choice == "5":
            test_get_spots_by_city()
        elif choice == "6":
            test_plan_trip_with_routing()
        elif choice == "7":
            test_search_spots_near_location()
        elif choice == "8":
            test_get_travel_time_estimation()
        elif choice == "9":
            test_generate_static_map()
        elif choice == "10":
            test_intelligent_trip_plan()
        elif choice == "11":
            test_all_amap_apis()
        elif choice == "12":
            run_complete_test()
        else:
            print("❌ 无效选择，请重新输入")

def run_complete_test():
    """运行完整测试套件"""
    print("\n🔬 运行完整测试套件")
    print("=" * 50)
    
    tests = [
        ("天气查询", test_get_weather),
        ("地理编码", test_get_geocode),
        ("路径规划", test_route_planning),
        ("附近搜索", test_search_nearby),
        ("城市景点", test_get_spots_by_city),
        ("智能规划", test_plan_trip_with_routing),
        ("附近景点", test_search_spots_near_location),
        ("时间估算", test_get_travel_time_estimation),
        ("静态地图", test_generate_static_map),
        ("提示模板", test_intelligent_trip_plan),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 测试: {test_name}")
        print("-" * 30)
        try:
            test_func()
            print(f"✅ {test_name}: 通过")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: 失败 - {str(e)}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    if passed == total:
        print("🎉 所有测试通过!")
    else:
        print("⚠️  部分测试失败，请检查错误信息")

def create_test_data():
    """创建测试数据目录结构"""
    print("\n📁 创建测试数据结构")
    print("=" * 50)
    
    data_dir = Path("./data")
    if not data_dir.exists():
        data_dir.mkdir()
        print("创建 ./data 目录")
    
    # 创建示例数据文件
    beijing_dir = data_dir / "北京" / "北京"
    beijing_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建示例景点数据
    sample_spots = [
        {
            "name": "故宫",
            "rating": 4.8,
            "address": "北京市东城区景山前街4号",
            "description": "明清两代的皇家宫殿，世界文化遗产",
            "province": "北京",
            "city": "北京"
        },
        {
            "name": "天安门广场",
            "rating": 4.7,
            "address": "北京市东城区东长安街",
            "description": "世界上最大的城市广场，中国的象征",
            "province": "北京",
            "city": "北京"
        },
        {
            "name": "颐和园",
            "rating": 4.6,
            "address": "北京市海淀区新建宫门路19号",
            "description": "中国现存最完整的皇家园林",
            "province": "北京",
            "city": "北京"
        }
    ]
    
    for i, spot in enumerate(sample_spots, 1):
        spot_file = beijing_dir / f"spot{i}.json"
        with open(spot_file, "w", encoding="utf-8") as f:
            json.dump(spot, f, ensure_ascii=False, indent=2)
    
    print(f"在 {beijing_dir} 中创建了3个示例景点")
    print("✅ 测试数据结构创建完成")

if __name__ == "__main__":
    print("🔧 旅游规划MCP服务测试工具")
    print("=" * 50)
    print("请选择测试模式:")
    print("1. 交互式测试")
    print("2. 运行完整测试")
    print("3. 创建测试数据")
    print("4. 退出")
    
    mode = input("\n请选择 (1-4): ").strip()
    
    if mode == "1":
        interactive_test()
    elif mode == "2":
        run_complete_test()
    elif mode == "3":
        create_test_data()
    elif mode == "4":
        print("👋 退出")
    else:
        print("❌ 无效选择")