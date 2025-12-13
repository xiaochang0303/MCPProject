import os
import requests
from dotenv import load_dotenv

# Load env variables if .env exists
load_dotenv()

# Configuration
NANO_BANANA_TOKEN = os.getenv("NANO_BANANA_TOKEN") or os.getenv("ACEDATA_TOKEN")
API_URL = "https://api.acedata.cloud/nano-banana/images"

def test_generate_image():
    if not NANO_BANANA_TOKEN:
        print("❌ Error: NANO_BANANA_TOKEN (or ACEDATA_TOKEN) not set.")
        print("Please set it in your environment or .env file.")
        print("Example: export NANO_BANANA_TOKEN=your_token_here")
        return

    # Sanitize token
    NANO_BANANA_TOKEN_CLEAN = NANO_BANANA_TOKEN.strip()
    print(NANO_BANANA_TOKEN_CLEAN)
    # exit()    
    print(f"✅ Token loaded (len={len(NANO_BANANA_TOKEN_CLEAN)}): {NANO_BANANA_TOKEN_CLEAN[:15]}...{NANO_BANANA_TOKEN_CLEAN[-4:]}")
    print("🚀 Sending request to Nano Banana API...")

    headers = {
        "authorization": f"Bearer {NANO_BANANA_TOKEN_CLEAN}",
        "accept": "application/json",
        "content-type": "application/json"
    }

    payload = {
        "action": "generate",
        "model": "nano-banana",
        "prompt": "A futuristic city with flying cars, cyberpunk style",
        "width": 1024,
        "height": 1024
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response:")
            print(data)
            
            # Check for image URL
            if "image_urls" in data:
                 print(f"Image URLs: {data['image_urls']}")
            elif "data" in data and isinstance(data["data"], list):
                 # Some APIs return list of objects
                 print(f"Data: {data['data']}")
            
        else:
            print("❌ Request failed.")
            print(response.text)

    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_generate_image()
