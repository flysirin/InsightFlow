from google import genai
from insightflow.core.config import settings

def main():
    print("🔑 Using Key:", settings.GOOGLE_KEYS_FREE[0][:10] + "...")
    client = genai.Client(api_key=settings.GOOGLE_KEYS_FREE[0])
    
    print("\n📡 Fetching models...")
    try:
        # The list method returns a Pager, which is iterable
        for m in client.models.list():
            # Check for supported_actions based on my code reading of types.py
            methods = getattr(m, 'supported_actions', [])
            print(f"   🔹 {m.name} | Display: {m.display_name} | Actions: {methods}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
