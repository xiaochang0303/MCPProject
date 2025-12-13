from mcp.server.fastmcp import FastMCP
import os
import json
import requests
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import base64
from io import BytesIO
import math

mcp = FastMCP("Tour Guide with AMap Integration")

# 配置信息
DATA_ROOT = "./data"   # JSON 数据根目录
AMAP_KEY = "8298dfe05050e8ca27709ef620da2a83"  # 高德地图API Key
AMAP_BASE_URL = "https://restapi.amap.com/v3"

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
                except Exception as e:
                    print(f"Error loading {fp}: {e}")
    return items


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """计算两个坐标点之间的距离（公里）使用Haversine公式"""
    R = 6371.0  # 地球半径，单位公里
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    distance = R * c
    return round(distance, 2)


@mcp.tool(
    name='get_weather',
    description='查询指定城市的实时天气信息'
)
def get_weather(city: str, extensions: str = "base") -> Dict[str, Any]:
    """
    查询指定城市的天气信息
    city: 城市名称，如"北京"
    extensions: "base"返回实时天气, "all"返回预报天气
    """
    url = f"{AMAP_BASE_URL}/weather/weatherInfo"
    params = {
        "key": AMAP_KEY,
        "city": city,
        "extensions": extensions,  # base: 实况天气, all: 预报天气
        "output": "JSON"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "1" and data.get("infocode") == "10000":
            if extensions == "base":
                lives = data.get("lives", [])
                if lives:
                    return {
                        "success": True,
                        "city": city,
                        "weather": lives[0],
                        "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
            else:
                forecasts = data.get("forecasts", [])
                if forecasts:
                    return {
                        "success": True,
                        "city": city,
                        "weather_forecast": forecasts[0],
                        "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
        
        return {
            "success": False,
            "message": f"天气查询失败: {data.get('info', '未知错误')}",
            "error_code": data.get("infocode")
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"网络请求失败: {str(e)}"
        }


@mcp.tool(
    name='get_geocode',
    description='地理编码：将地址转换为经纬度坐标'
)
def get_geocode(address: str, city: str = None) -> Dict[str, Any]:
    """
    获取地址的经纬度坐标
    address: 详细地址
    city: 城市名称（可选，用于限定范围）
    """
    url = f"{AMAP_BASE_URL}/geocode/geo"
    params = {
        "key": AMAP_KEY,
        "address": address,
        "output": "JSON"
    }
    
    if city:
        params["city"] = city
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "1" and data.get("geocodes"):
            geocode = data["geocodes"][0]
            location = geocode.get("location")
            if location:
                lng, lat = location.split(",")
                return {
                    "success": True,
                    "address": address,
                    "location": {
                        "longitude": float(lng),
                        "latitude": float(lat)
                    },
                    "formatted_address": geocode.get("formatted_address"),
                    "country": geocode.get("country"),
                    "province": geocode.get("province"),
                    "city": geocode.get("city"),
                    "district": geocode.get("district")
                }
        
        return {
            "success": False,
            "message": f"地理编码失败: {data.get('info', '未找到地址')}"
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"网络请求失败: {str(e)}"
        }


@mcp.tool(
    name='route_planning',
    description='路径规划：计算两点之间的路线，提供多种交通方式的规划'
)
def route_planning(origin: str, destination: str, 
                   city: str = None, 
                   strategy: int = 0) -> Dict[str, Any]:
    """
    路径规划工具
    origin: 起点地址
    destination: 终点地址
    city: 城市名称（可选）
    strategy: 策略 0-速度最快 1-费用最低 2-距离最短 3-不走高速 4-躲避拥堵 5-多策略
    """
    # 先获取起点和终点的坐标
    origin_geo = get_geocode(origin, city)
    dest_geo = get_geocode(destination, city)
    
    if not origin_geo.get("success") or not dest_geo.get("success"):
        return {
            "success": False,
            "message": "无法获取起点或终点的坐标",
            "origin_error": origin_geo.get("message"),
            "dest_error": dest_geo.get("message")
        }
    
    origin_loc = origin_geo["location"]
    dest_loc = dest_geo["location"]
    
    # 计算各种交通方式的路线
    results = {}
    
    # 驾车路径规划
    url = f"{AMAP_BASE_URL}/direction/driving"
    params = {
        "key": AMAP_KEY,
        "origin": f"{origin_loc['longitude']},{origin_loc['latitude']}",
        "destination": f"{dest_loc['longitude']},{dest_loc['latitude']}",
        "strategy": strategy,
        "extensions": "all",
        "output": "JSON"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "1":
            route = data.get("route", {})
            paths = route.get("paths", [])
            if paths:
                path = paths[0]
                # 估算费用（简单估算）
                distance = float(path.get("distance", 0)) / 1000  # 转换为公里
                duration = float(path.get("duration", 0)) / 60  # 转换为分钟
                
                # 出租车费用估算（假设3公里内14元，超过部分每公里2.5元）
                taxi_cost = 14
                if distance > 3:
                    taxi_cost += (distance - 3) * 2.5
                
                # 油费估算（假设百公里油耗8L，油价8元/L）
                fuel_cost = (distance / 100) * 8 * 8
                
                results["driving"] = {
                    "distance_km": round(distance, 2),
                    "duration_min": round(duration, 2),
                    "taxi_cost_yuan": round(taxi_cost, 2),
                    "fuel_cost_yuan": round(fuel_cost, 2),
                    "steps": path.get("steps", []),
                    "strategy": strategy
                }
        
        # 步行路径规划
        url = f"{AMAP_BASE_URL}/direction/walking"
        params = {
            "key": AMAP_KEY,
            "origin": f"{origin_loc['longitude']},{origin_loc['latitude']}",
            "destination": f"{dest_loc['longitude']},{dest_loc['latitude']}",
            "output": "JSON"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "1":
            route = data.get("route", {})
            paths = route.get("paths", [])
            if paths:
                path = paths[0]
                distance = float(path.get("distance", 0)) / 1000
                duration = float(path.get("duration", 0)) / 60
                
                results["walking"] = {
                    "distance_km": round(distance, 2),
                    "duration_min": round(duration, 2),
                    "steps": path.get("steps", [])
                }
        
        # 公交路径规划
        url = f"{AMAP_BASE_URL}/direction/transit/integrated"
        params = {
            "key": AMAP_KEY,
            "origin": f"{origin_loc['longitude']},{origin_loc['latitude']}",
            "destination": f"{dest_loc['longitude']},{dest_loc['latitude']}",
            "city": city if city else "北京",  # 默认北京
            "output": "JSON"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "1":
            route = data.get("route", {})
            transits = route.get("transits", [])
            if transits:
                transit = transits[0]
                distance = float(transit.get("distance", 0)) / 1000
                duration = float(transit.get("duration", 0)) / 60
                cost = float(transit.get("cost", 0))
                
                results["transit"] = {
                    "distance_km": round(distance, 2),
                    "duration_min": round(duration, 2),
                    "cost_yuan": cost,
                    "segments": transit.get("segments", [])
                }
        
        return {
            "success": True,
            "origin": origin_geo.get("formatted_address"),
            "destination": dest_geo.get("formatted_address"),
            "distance_km": round(calculate_distance(
                origin_loc["latitude"], origin_loc["longitude"],
                dest_loc["latitude"], dest_loc["longitude"]
            ), 2),
            "routes": results,
            "recommendation": _recommend_route(results)
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"路径规划失败: {str(e)}"
        }


def _recommend_route(routes: Dict[str, Any]) -> Dict[str, Any]:
    """根据路线结果推荐最佳方式"""
    recommendations = []
    
    if "walking" in routes:
        walk = routes["walking"]
        if walk["distance_km"] <= 3:  # 3公里内推荐步行
            recommendations.append({
                "method": "walking",
                "reason": f"距离较近 ({walk['distance_km']}公里)，适合步行锻炼身体",
                "duration": walk["duration_min"],
                "cost": 0
            })
    
    if "transit" in routes:
        transit = routes["transit"]
        recommendations.append({
            "method": "transit",
            "reason": f"公共交通经济实惠，费用 {transit['cost_yuan']}元",
            "duration": transit["duration_min"],
            "cost": transit["cost_yuan"]
        })
    
    if "driving" in routes:
        drive = routes["driving"]
        recommendations.append({
            "method": "driving/taxi",
            "reason": f"最快方式，出租车约{drive['taxi_cost_yuan']}元，自驾油费约{drive['fuel_cost_yuan']}元",
            "duration": drive["duration_min"],
            "taxi_cost": drive["taxi_cost_yuan"],
            "fuel_cost": drive["fuel_cost_yuan"]
        })
    
    # 按持续时间排序推荐
    recommendations.sort(key=lambda x: x["duration"])
    
    return {
        "best_option": recommendations[0] if recommendations else None,
        "all_options": recommendations
    }


@mcp.tool(
    name='search_nearby',
    description='搜索指定地点附近的POI（兴趣点）'
)
def search_nearby(location: str, keywords: str = "景点", 
                  radius: int = 3000, city: str = None) -> Dict[str, Any]:
    """
    搜索指定地点附近的POI
    location: 中心点地址或坐标（格式：经度,纬度）
    keywords: 搜索关键词，如"景点、餐厅、酒店"
    radius: 搜索半径，单位米，最大50000
    city: 城市名称（可选）
    """
    # 如果location不是坐标格式，尝试地理编码
    if "," not in location:
        geo_result = get_geocode(location, city)
        if not geo_result.get("success"):
            return {
                "success": False,
                "message": f"无法解析地址: {location}"
            }
        location_str = f"{geo_result['location']['longitude']},{geo_result['location']['latitude']}"
    else:
        location_str = location
    
    url = f"{AMAP_BASE_URL}/place/around"
    params = {
        "key": AMAP_KEY,
        "location": location_str,
        "keywords": keywords,
        "radius": radius,
        "output": "JSON",
        "extensions": "all"
    }
    
    if city:
        params["city"] = city
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "1":
            pois = data.get("pois", [])
            
            # 处理POI数据
            processed_pois = []
            for poi in pois:
                # 计算距离（如果提供了中心点坐标）
                distance = None
                if "," in location_str:
                    center_lng, center_lat = map(float, location_str.split(","))
                    poi_location = poi.get("location", "").split(",")
                    if len(poi_location) == 2:
                        poi_lng, poi_lat = map(float, poi_location)
                        distance = calculate_distance(center_lat, center_lng, poi_lat, poi_lng)
                
                processed_pois.append({
                    "id": poi.get("id"),
                    "name": poi.get("name"),
                    "type": poi.get("type"),
                    "typecode": poi.get("typecode"),
                    "address": poi.get("address"),
                    "location": {
                        "longitude": float(poi_location[0]) if len(poi_location) == 2 else None,
                        "latitude": float(poi_location[1]) if len(poi_location) == 2 else None
                    },
                    "distance_km": distance,
                    "pcode": poi.get("pcode"),  # 省份编码
                    "pname": poi.get("pname"),  # 省份名称
                    "citycode": poi.get("citycode"),
                    "cityname": poi.get("cityname"),
                    "adcode": poi.get("adcode"),
                    "adname": poi.get("adname"),
                    "tel": poi.get("tel"),
                    "website": poi.get("website")
                })
            
            # 按距离排序
            processed_pois.sort(key=lambda x: x["distance_km"] or float('inf'))
            
            return {
                "success": True,
                "location": location,
                "keywords": keywords,
                "radius_m": radius,
                "count": len(processed_pois),
                "pois": processed_pois[:20],  # 返回前20个结果
                "suggestion": {
                    "nearby_types": _analyze_poi_types(processed_pois),
                    "recommended_radius": min(radius * 2, 50000) if len(processed_pois) < 5 else radius
                }
            }
        
        return {
            "success": False,
            "message": f"搜索失败: {data.get('info', '未知错误')}",
            "error_code": data.get("infocode")
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"网络请求失败: {str(e)}"
        }


def _analyze_poi_types(pois: List[Dict[str, Any]]) -> Dict[str, int]:
    """分析POI类型分布"""
    type_count = {}
    for poi in pois:
        poi_type = poi.get("type", "未知")
        if poi_type in type_count:
            type_count[poi_type] += 1
        else:
            type_count[poi_type] = 1
    return type_count


@mcp.tool(
    name='get_spots_by_province',
    description='根据省份名称获取该省所有景点数据（从本地JSON文件读取），并整合天气信息'
)
def get_spots_by_province(province: str, include_weather: bool = True) -> Dict[str, Any]:
    """获取省份景点并整合天气信息"""
    target_path = os.path.join(DATA_ROOT, province)
    result = load_json_files_in_path(target_path)
    
    response = {
        "province": province,
        "spots": result,
        "count": len(result)
    }
    
    # 如果包含天气信息，获取省会天气
    if include_weather and result:
        # 尝试从景点中获取城市信息
        cities = set()
        for spot in result:
            if 'city' in spot:
                cities.add(spot['city'])
        
        # 获取第一个城市的天气
        if cities:
            city = list(cities)[0]
            weather_info = get_weather(city)
            if weather_info.get("success"):
                response["weather"] = weather_info.get("weather", {})
                response["weather_city"] = city
    
    return response


@mcp.tool(
    name='get_spots_by_city',
    description='根据城市名称获取景点数据（从本地JSON文件读取），并整合天气和附近设施信息'
)
def get_spots_by_city(province: str, city: str, 
                      include_weather: bool = True,
                      include_nearby: bool = False) -> Dict[str, Any]:
    """获取城市景点，可整合天气和附近设施"""
    target_path = os.path.join(DATA_ROOT, province, city)
    result = load_json_files_in_path(target_path)

    response = {
        "province": province,
        "city": city,
        "spots": result,
        "count": len(result)
    }
    
    # 获取天气信息
    if include_weather:
        weather_info = get_weather(city)
        if weather_info.get("success"):
            response["weather"] = weather_info.get("weather", {})
    
    # 获取景点附近设施
    if include_nearby and result:
        nearby_analysis = []
        for spot in result[:3]:  # 分析前3个景点
            spot_name = spot.get("name")
            if 'address' in spot:
                nearby_result = search_nearby(spot['address'], "餐厅|酒店|停车场", 1000, city)
                if nearby_result.get("success"):
                    nearby_analysis.append({
                        "spot": spot_name,
                        "nearby_facilities": nearby_result.get("suggestion", {}).get("nearby_types", {}),
                        "poi_count": nearby_result.get("count", 0)
                    })
        
        if nearby_analysis:
            response["nearby_analysis"] = nearby_analysis
    
    return response


@mcp.tool(
    name='plan_trip_with_routing',
    description='结合本地景点数据和高德API的智能旅游规划，包含路线规划和天气考虑'
)
def plan_trip_with_routing(province: str, city: str, days: int = 3) -> Dict[str, Any]:
    """
    智能旅游规划：结合景点数据、路线规划和天气信息
    """
    # 获取景点数据
    spots_data = get_spots_by_city(province, city, include_weather=True, include_nearby=True)
    
    if spots_data["count"] == 0:
        return {
            "success": False,
            "message": f"未找到{city}的景点数据"
        }
    
    spots = spots_data["spots"]
    weather = spots_data.get("weather", {})
    
    # 按评分排序
    sorted_spots = sorted(spots, key=lambda x: float(x.get("rating", 0)), reverse=True)
    
    # 生成旅游规划
    daily_plans = []
    spots_per_day = min(len(sorted_spots), days * 3)  # 每天最多安排3个景点
    
    for day in range(1, days + 1):
        day_spots = sorted_spots[(day-1)*3:day*3]
        if not day_spots:
            break
        
        day_plan = {
            "day": day,
            "spots": [],
            "estimated_time_hours": 0,
            "travel_advice": []
        }
        
        for i, spot in enumerate(day_spots):
            # 获取景点地址
            spot_address = spot.get("address", city)
            
            # 如果是第一个景点，不需要路线规划
            if i == 0:
                travel_info = {"method": "starting_point", "duration": 0}
            else:
                # 计算从前一个景点到这个景点的路线
                prev_spot = day_spots[i-1]
                prev_address = prev_spot.get("address", city)
                
                route_result = route_planning(
                    prev_address, 
                    spot_address,
                    city=city,
                    strategy=5  # 多策略
                )
                
                if route_result.get("success"):
                    best_route = route_result.get("recommendation", {}).get("best_option", {})
                    travel_info = {
                        "from": prev_spot.get("name"),
                        "method": best_route.get("method", "unknown"),
                        "duration_min": best_route.get("duration", 0),
                        "cost_yuan": best_route.get("cost", 0) or best_route.get("taxi_cost", 0)
                    }
                else:
                    travel_info = {"method": "walking", "duration_min": 30, "cost_yuan": 0}
            
            day_plan["spots"].append({
                "name": spot.get("name"),
                "rating": spot.get("rating"),
                "address": spot_address,
                "description": spot.get("description", ""),
                "estimated_visit_hours": 2,  # 假设每个景点参观2小时
                "travel_info": travel_info if i > 0 else None
            })
            
            # 累加时间
            day_plan["estimated_time_hours"] += 2
            if i > 0:
                day_plan["estimated_time_hours"] += travel_info.get("duration_min", 0) / 60
        
        # 添加天气建议
        if weather:
            temperature = weather.get("temperature", "未知")
            weather_condition = weather.get("weather", "未知")
            day_plan["weather_advice"] = f"今日气温{temperature}°C，天气{weather_condition}，建议适当穿衣"
        
        daily_plans.append(day_plan)
    
    # 计算总花费估算
    total_cost = 0
    transportation_cost = 0
    
    for plan in daily_plans:
        for spot in plan["spots"]:
            if spot["travel_info"] and "cost_yuan" in spot["travel_info"]:
                transportation_cost += spot["travel_info"]["cost_yuan"]
    
    # 餐饮住宿估算
    food_cost = days * 100  # 假设每天餐饮100元
    accommodation_cost = (days - 1) * 200 if days > 1 else 0  # 假设住宿200元/晚
    
    total_cost = transportation_cost + food_cost + accommodation_cost
    
    return {
        "success": True,
        "province": province,
        "city": city,
        "days": days,
        "total_spots": spots_per_day,
        "weather_summary": weather,
        "daily_plans": daily_plans,
        "cost_estimation": {
            "transportation_yuan": round(transportation_cost, 2),
            "food_yuan": food_cost,
            "accommodation_yuan": accommodation_cost,
            "total_yuan": total_cost,
            "budget_suggestion": _get_budget_suggestion(total_cost)
        },
        "recommendations": _generate_trip_recommendations(spots_data, weather, days)
    }


def _get_budget_suggestion(total_cost: float) -> str:
    """根据总花费给出预算建议"""
    if total_cost < 500:
        return "经济型旅行，适合背包客和学生"
    elif total_cost < 1500:
        return "舒适型旅行，适合家庭和情侣"
    elif total_cost < 3000:
        return "豪华型旅行，适合商务和度假"
    else:
        return "奢华型旅行，适合高端定制游"


def _generate_trip_recommendations(spots_data: Dict, weather: Dict, days: int) -> List[str]:
    """生成旅游建议"""
    recommendations = []
    
    # 天气相关建议
    if weather:
        temperature = float(weather.get("temperature", 20))
        weather_cond = weather.get("weather", "")
        
        if temperature > 30:
            recommendations.append("天气炎热，建议早晚出行，中午休息，注意防晒补水")
        elif temperature < 10:
            recommendations.append("天气较冷，请注意保暖，穿戴厚外套")
        
        if "雨" in weather_cond:
            recommendations.append("有雨，建议携带雨具，安排室内活动")
        elif "晴" in weather_cond:
            recommendations.append("天气晴朗，适合户外活动和拍照")
    
    # 景点相关建议
    spots_count = spots_data.get("count", 0)
    if spots_count > days * 3:
        recommendations.append(f"景点较多，建议延长行程或选择重点景点参观")
    
    # 附近设施建议
    nearby_analysis = spots_data.get("nearby_analysis", [])
    if nearby_analysis:
        for analysis in nearby_analysis:
            facilities = analysis.get("nearby_facilities", {})
            if "餐厅" in str(facilities):
                recommendations.append(f"{analysis['spot']}附近有餐厅，方便就餐")
            if "停车场" in str(facilities):
                recommendations.append(f"{analysis['spot']}附近有停车场，适合自驾游客")
    
    return recommendations[:5]  # 返回前5条建议


@mcp.tool(
    name='search_spots_near_location',
    description='搜索指定位置附近的景点（结合本地数据和高德API）'
)
def search_spots_near_location(location: str, radius_km: float = 5, 
                               min_rating: float = 3.5) -> Dict[str, Any]:
    """
    搜索指定位置附近的景点，结合高德API和本地数据
    """
    # 搜索附近的POI
    nearby_result = search_nearby(location, "景点|公园|名胜古迹", int(radius_km * 1000))
    
    if not nearby_result.get("success"):
        return nearby_result
    
    # 加载所有本地景点数据
    all_spots = []
    if os.path.exists(DATA_ROOT):
        for province in os.listdir(DATA_ROOT):
            province_path = os.path.join(DATA_ROOT, province)
            if os.path.isdir(province_path):
                all_spots.extend(load_json_files_in_path(province_path))
    
    # 匹配和筛选景点
    matched_spots = []
    for poi in nearby_result.get("pois", []):
        poi_name = poi.get("name", "")
        poi_city = poi.get("cityname", "")
        
        # 在本地数据中查找匹配的景点
        for spot in all_spots:
            spot_name = spot.get("name", "")
            spot_city = spot.get("city", "")
            
            # 简单的名称匹配
            if (poi_name in spot_name or spot_name in poi_name) and poi_city == spot_city:
                # 检查评分
                spot_rating = float(spot.get("rating", 0))
                if spot_rating >= min_rating:
                    matched_spots.append({
                        "name": spot_name,
                        "rating": spot_rating,
                        "address": spot.get("address", ""),
                        "description": spot.get("description", ""),
                        "distance_km": poi.get("distance_km"),
                        "city": spot_city,
                        "province": spot.get("province", ""),
                        "poi_info": poi
                    })
                break
    
    # 按距离排序
    matched_spots.sort(key=lambda x: x.get("distance_km", float('inf')))
    
    return {
        "success": True,
        "location": location,
        "radius_km": radius_km,
        "nearby_poi_count": nearby_result.get("count", 0),
        "matched_spots_count": len(matched_spots),
        "spots": matched_spots[:10],  # 返回前10个
        "search_summary": {
            "average_rating": round(sum(s["rating"] for s in matched_spots) / len(matched_spots), 2) if matched_spots else 0,
            "closest_spot": matched_spots[0]["name"] if matched_spots else None,
            "best_rated_spot": max(matched_spots, key=lambda x: x["rating"])["name"] if matched_spots else None
        }
    }


@mcp.tool(
    name='get_travel_time_estimation',
    description='估算多个景点之间的旅行时间，优化游览顺序'
)
def get_travel_time_estimation(spots: List[str], start_location: str = None) -> Dict[str, Any]:
    """
    估算多个景点间的旅行时间，提供最优路线建议
    spots: 景点名称列表
    start_location: 起始位置（可选）
    """
    if not spots:
        return {"success": False, "message": "请提供至少一个景点"}
    
    # 获取景点地址
    spot_addresses = []
    for spot_name in spots:
        # 这里可以扩展为从本地数据或高德API获取地址
        # 简化处理：假设地址就是名称
        spot_addresses.append(spot_name)
    
    # 简单的旅行商问题近似解法
    if start_location:
        locations = [start_location] + spot_addresses
    else:
        locations = spot_addresses
    
    # 估算每对地点之间的时间
    travel_matrix = {}
    routes_summary = []
    
    for i in range(len(locations) - 1):
        from_loc = locations[i]
        to_loc = locations[i + 1]
        
        route = route_planning(from_loc, to_loc, strategy=0)
        
        if route.get("success"):
            best_option = route.get("recommendation", {}).get("best_option", {})
            travel_matrix[f"{from_loc}→{to_loc}"] = {
                "duration_min": best_option.get("duration", 30),
                "method": best_option.get("method", "walking"),
                "cost_yuan": best_option.get("cost", 0) or best_option.get("taxi_cost", 0)
            }
            
            routes_summary.append({
                "from": from_loc,
                "to": to_loc,
                "duration_min": best_option.get("duration", 30),
                "method": best_option.get("method", "walking"),
                "cost_yuan": best_option.get("cost", 0) or best_option.get("taxi_cost", 0)
            })
    
    # 计算总时间和花费
    total_duration = sum(r["duration_min"] for r in routes_summary)
    total_cost = sum(r["cost_yuan"] for r in routes_summary)
    
    # 游览时间估算（假设每个景点2小时）
    visit_hours = len(spots) * 2 * 60  # 转换为分钟
    
    total_time_minutes = total_duration + visit_hours
    
    return {
        "success": True,
        "spots_count": len(spots),
        "total_travel_time_min": round(total_duration, 2),
        "total_visit_time_min": visit_hours,
        "total_time_min": round(total_time_minutes, 2),
        "estimated_hours": round(total_time_minutes / 60, 1),
        "total_cost_yuan": round(total_cost, 2),
        "routes": routes_summary,
        "recommendation": {
            "best_order": spots,  # 可以在这里实现更智能的排序算法
            "estimated_start_time": "08:00",
            "estimated_end_time": _calculate_end_time(total_time_minutes),
            "breaks_suggested": len(spots) // 3  # 每3个景点建议休息一次
        }
    }


def _calculate_end_time(total_minutes: float) -> str:
    """计算结束时间"""
    from datetime import datetime, timedelta
    
    start_time = datetime.now().replace(hour=8, minute=0, second=0)
    end_time = start_time + timedelta(minutes=total_minutes)
    return end_time.strftime("%H:%M")


# 保留原有的可视化工具（可以添加高德地图的静态地图功能）
@mcp.tool(
    name='generate_static_map',
    description='生成指定位置的静态地图（使用高德地图API）'
)
def generate_static_map(location: str, zoom: int = 15, 
                       size: str = "400 * 300", markers: str = None) -> Dict[str, Any]:
    """
    生成静态地图
    location: 中心点坐标或地址
    zoom: 缩放级别 1-17
    size: 图片大小，格式"宽*高"
    markers: 标记点，格式"经度,纬度,标记样式|..."
    """
    # 如果是地址，先转换为坐标
    if "," not in location:
        geo_result = get_geocode(location)
        if not geo_result.get("success"):
            return {"success": False, "message": "无法解析地址"}
        location = f"{geo_result['location']['longitude']},{geo_result['location']['latitude']}"
    
    url = f"https://restapi.amap.com/v3/staticmap"
    params = {
        "key": AMAP_KEY,
        "location": location,
        "zoom": zoom,
        "size": size,
        "scale": 2  # 2为高清
    }
    
    if markers:
        params["markers"] = markers
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        # 返回Base64编码的地图图片
        img_base64 = base64.b64encode(response.content).decode('utf-8')
        
        return {
            "success": True,
            "location": location,
            "image_base64": img_base64,
            "format": "png",
            "size": size,
            "zoom": zoom
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"生成地图失败: {str(e)}"
        }


@mcp.prompt(
    name='intelligent_trip_plan',
    description='智能旅游规划：根据用户需求生成完整的旅游计划，包含天气、路线、预算等'
)
def intelligent_trip_plan(destination: str, days: int, budget: float = None) -> str:
    return f"""你是一个专业的智能旅游规划助手。请为以下旅游需求提供详细规划：

目的地：{destination}
天数：{days}天
预算：{'不限' if budget is None else f'{budget}元'}

请结合以下维度进行分析：
1. 天气情况与穿衣建议
2. 每日行程安排（景点、餐饮、住宿建议）
3. 交通路线规划（最优路线、交通方式、时间预估）
4. 预算分配明细
5. 必带物品清单
6. 注意事项与安全提示
7. 应急联系方式建议

请提供详细、实用、个性化的旅游规划方案。"""


# 主函数
if __name__ == "__main__":
    # 打印可用工具列表
    print("🚀 启动 Tour Guide MCP 服务器 (集成高德地图API)")
    print("   服务名称: Tour Guide with AMap Integration")
    print("   高德地图API Key: 已配置")
    print("   数据目录: ./data")
    print("   可用工具:")
    print("     1. get_weather - 查询城市天气")
    print("     2. get_geocode - 地址转坐标")
    print("     3. route_planning - 路径规划")
    print("     4. search_nearby - 附近地点搜索")
    print("     5. get_spots_by_province - 省份景点查询")
    print("     6. get_spots_by_city - 城市景点查询")
    print("     7. plan_trip_with_routing - 智能旅游规划")
    print("     8. search_spots_near_location - 附近景点搜索")
    print("     9. get_travel_time_estimation - 旅行时间估算")
    print("     10. generate_static_map - 静态地图生成")
    print("     11. intelligent_trip_plan - 智能旅游规划提示")
    
    import sys
    if "--sse" in sys.argv or os.getenv("MCP_TRANSPORT") == "sse":
        print("   传输协议: Server-Sent Events (SSE)")
        mcp.run(transport="sse")
    else:
        mcp.run()