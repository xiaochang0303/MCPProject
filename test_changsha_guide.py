import os
import requests
from dotenv import load_dotenv

load_dotenv()

NANO_BANANA_TOKEN = os.getenv("NANO_BANANA_TOKEN") or os.getenv("ACEDATA_TOKEN")
API_URL = "https://api.acedata.cloud/nano-banana/images"

def generate_changsha_guide():
    if not NANO_BANANA_TOKEN:
        print("❌ Token not found in .env")
        return

    # Clean token
    token = NANO_BANANA_TOKEN.strip()
    
    prompt = (
        "A detailed travel guide infographic for Changsha, China. "
        "The image is divided into 4 vertical sections (rows). "
        "Row 1: Morning scene at Yuelu Mountain, misty and serene with autumn leaves. "
        "Row 2: Noon scene at Orange Isle (Juzizhou) with the giant Mao Zedong statue under bright sunlight. "
        "Row 3: Evening scene at Pozi Street or Wenheyou, bustling night market with neon lights and spicy food like Stinky Tofu. "
        "Row 4: Weather icons showing partly cloudy sky, 20°C, and clothing recommendation icons (light jacket, walking shoes). "
        "High quality, realistic style, vibrant colors, clear layout."
    )

    print(f"🚀 Generating Changsha Guide with prompt:\n{prompt}\n")

    headers = {
        "authorization": f"Bearer {token}",
        "accept": "application/json",
        "content-type": "application/json"
    }

    payload = {
        "action": "generate",
        "model": "nano-banana",
        "prompt": prompt,
        "width": 1024,
        "height": 2048  # Taller aspect ratio for 4 rows
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response:")
            print(data)
            if "image_urls" in data:
                print(f"\nImage URL: {data['image_urls'][0]}")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_changsha_guide()
