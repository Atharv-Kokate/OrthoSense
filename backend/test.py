import os
from dotenv import load_dotenv
from groq import AsyncGroq
import asyncio

async def main():
    load_dotenv()
    key = os.environ.get("GROQ_API_KEY")
    print(f"Loaded Key: {key}")
    try:
        client = AsyncGroq(api_key=key)
        res = await client.chat.completions.create(
            messages=[{"role": "user", "content": "hi"}],
            model="llama3-8b-8192"
        )
        print("SUCCESS:", res.choices[0].message.content)
    except Exception as e:
        print("EXCEPTION:", repr(e))

if __name__ == "__main__":
    asyncio.run(main())
