import matplotlib.pyplot as plt
import matplotlib
from tourmcp import get_spots_by_city

# Set Chinese font for matplotlib
matplotlib.rcParams['font.family'] = ['Heiti TC'] # Adjust to a font available on your system that supports Chinese characters

def visualize_city_spots(province: str, city: str):
    """
    Retrieves scenic spot data for a given city and visualizes it.
    """
    print(f"Retrieving scenic spot data for {city}, {province}...")
    data = get_spots_by_city(province, city)

    spots = data.get("spots", [])
    if not spots:
        print(f"No scenic spots found for {city}, {province}.")
        return

    spot_names = [spot.get("name", "Unknown") for spot in spots]
    spot_ratings = [spot.get("rating", 0) for spot in spots]

    # Create a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(spot_names, spot_ratings, color='skyblue')
    plt.xlabel('Scenic Spot')
    plt.ylabel('Rating')
    plt.title(f'Scenic Spot Ratings in {city}, {province}')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Example usage (you can change these values)
    visualize_city_spots("浙江", "舟山")
