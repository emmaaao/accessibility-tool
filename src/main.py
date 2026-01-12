from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

try:
    print("\n Testing connection to Claude API...")

    client = Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[
            {"role": "user", "content": "API connection successful!"}
        ]
    )

    print("\nSUCCESS! API is working!")
    print(f" Claude's response: {message.content[0].text}")

except Exception as e:
    print(f"\n ERROR: {e}")
