from mcp.server.fastmcp import FastMCP
import matplotlib.pyplot as plt
from visualize_spots import visualize_city_spots
import os

# Initialize FastMCP
mcp = FastMCP("Image Generation MCP")

OUTPUT_DIR = os.path.join(os.getcwd(), "generated_images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

@mcp.tool(
    name='generate_trip_visualization',
    description='Generates a visual representation of the trip plan using the "Nano Banana" model (Mocked).'
)
def generate_trip_visualization(trip_plan: str) -> str:
    """
    Mock implementation of 'Nano Banana' image generation.
    Generates a simple image with the trip plan text overlaid, simulating a route map.
    """
    print(f"Generating image for plan: {trip_plan[:50]}...")
    
    # Create a simple figure with text
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.text(0.5, 0.5, "Trip Plan Visualization\n(Nano Banana Mock)\n\n" + trip_plan[:100] + "...", 
            ha='center', va='center', fontsize=12, wrap=True)
    ax.axis('off')
    
    filename = f"trip_vis_{hash(trip_plan)}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(filepath)
    plt.close()
    
    return filepath

@mcp.tool(
    name='generate_stats_chart',
    description='Generates a statistical chart of scenic spots for a city.'
)
def generate_stats_chart(province: str, city: str) -> str:
    """
    Wraps visualize_city_spots to generate a chart and save it.
    """
    # Note: visualize_city_spots in original file calls plt.show(). 
    # We might need to modify it or just implement similar logic here to save instead of show.
    # For robust MCP, I'll reimplement the plotting here to ensure saving.
    
    from tourmcp import get_spots_by_city
    data = get_spots_by_city(province, city)
    spots = data.get("spots", [])
    
    if not spots:
        return "No spots found"

    spot_names = [spot.get("name", "Unknown") for spot in spots]
    spot_ratings = [spot.get("rating", 0) for spot in spots]

    plt.figure(figsize=(10, 6))
    plt.bar(spot_names, spot_ratings, color='skyblue')
    plt.xlabel('Scenic Spot')
    plt.ylabel('Rating')
    plt.title(f'Scenic Spot Ratings in {city}, {province}')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    filename = f"stats_{province}_{city}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(filepath)
    plt.close()
    
    return filepath

if __name__ == "__main__":
    mcp.run()
