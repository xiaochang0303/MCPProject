import os
import time
from tourmcp import get_spots_by_city, plan_trip
from image_gen_mcp import generate_trip_visualization, generate_stats_chart
from xhs_mcp import publish_note

# In a real MCP architecture, these would be called over RPC. 
# Here we simulate the agent calling them as tools.

def main():
    print("=== Starting Travel Content Automation Workflow ===")
    
    # 1. Define Request
# ... (imports remain)
from tourmcp import get_spots_by_city, get_spots_by_cities, plan_trip

def main():
    print("=== Starting Travel Content Automation Workflow ===")
    
    # 1. Interactive Request
    print("Please enter the travel destination info:")
    PROVINCE = input("Province/Region (e.g. 浙江): ").strip()
    if not PROVINCE:
        PROVINCE = "浙江" # Default
        
    cities_input = input("Cities (comma separated, e.g. 杭州, 宁波). Leave empty for single city mode or auto-select: ").strip()
    
    spots_data = {}
    
    if "," in cities_input or cities_input:
        # Multi-city mode
        CITIES = [c.strip() for c in cities_input.split(",") if c.strip()]
        if len(CITIES) == 1:
            CITY = CITIES[0]
            print(f"Goal: Plan a trip to single city {CITY}, {PROVINCE}.")
            print("\n--- Step 1: Getting Travel Data ---")
            spots_data = get_spots_by_city(PROVINCE, CITY)
        else:
            CITY = " & ".join(CITIES) # For display/title
            print(f"Goal: Plan a multi-city trip to {CITY} in {PROVINCE}.")
            print("\n--- Step 1: Getting Travel Data ---")
            spots_data = get_spots_by_cities(PROVINCE, CITIES)
            
    else:
        # Fallback / Single City Default
        CITY = input("Single City Name (e.g. 舟山): ").strip() or "舟山"
        print(f"Goal: Plan a trip to {CITY}, {PROVINCE}.")
        print("\n--- Step 1: Getting Travel Data ---")
        spots_data = get_spots_by_city(PROVINCE, CITY)

    print(f"Found {spots_data.get('count')} spots.")
    
    # Simple logic to create a plan message
    # For multi-city, we might want more spots to cover all cities
    all_spots = spots_data.get('spots', [])
    # Limit to reasonable amount for prompt (e.g. top 3 per city if multi-city?)
    selected_spots = all_spots[:10] 
    
    spots_list_str = str(selected_spots)
    
    print("\n--- Step 2: Planning Trip ---")
    trip_plan_prompt = plan_trip(spots_list_str)
    
    # Simulate LLM Response with Multi-City logic
    # In reality, this string comes from the LLM based on trip_plan_prompt
    if " & " in CITY:
        trip_heading = f"【{PROVINCE}多地游：{CITY} 深度攻略】"
        route_text = "Route: " + " -> ".join([s['name'] for s in selected_spots[:3]]) + "..."
    else:
        trip_heading = f"【{CITY}两日游完美攻略】"
        route_text = "Day 1: " + " -> ".join([s['name'] for s in selected_spots[:2]])
        
    trip_plan_content = f"""
    {trip_heading}
    {route_text}
    
    推荐理由：一次打卡多个宝藏城市，感受{PROVINCE}的不同风情！
    #旅游 #{PROVINCE} #{CITY.replace(' & ', ' #')}
    """
    print("Generated Plan Content:")
    print(trip_plan_content)

    # 3. Call Image Gen MCP
    print("\n--- Step 3: Generating Visuals ---")
    # Generate Route Visualization
    vis_image_path = generate_trip_visualization(trip_plan_content)
    print(f"Generated Visualization: {vis_image_path}")
    
    # Generate Stats Chart
    stats_image_path = generate_stats_chart(PROVINCE, CITY)
    print(f"Generated Stats Chart: {stats_image_path}")

    # 4. Call XHS Publisher MCP
    print("\n--- Step 4: Publishing to Xiaohongshu ---")
    # We can publish multiple notes or one with multiple images. 
    # The current publish_note tool takes a single media path.
    # Let's publish the Visualization.
    
    # NOTE: This requires the Selenium driver to start, which might take time/require interaction.
    # We will wrap this in a try/except or user confirmation in a real scenario.
    print("Simulating Publish... (This will open Chrome if configured)")
    
    # Uncomment to actually publish
    publish_note(
        title=f"Copy of {CITY} Travel Guide 🌊",
        content=trip_plan_content,
        media_path=vis_image_path,
        topics=["#Travel", f"#{CITY}"]
    )
    
    # print("Publishing steps are commented out to prevent accidental posting during test.")
    # print(f"Image to publish: {vis_image_path}")
    # print("Review the code to uncomment publishing.")

if __name__ == "__main__":
    main()
