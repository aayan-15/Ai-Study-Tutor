import os, time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROK_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

start = time.time()

reply = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "Hello! Introduce yourself in one line."}],
)

print(reply.choices[0].message.content)
print(f"Time: {time.time() - start:.2f} seconds")