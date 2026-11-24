
import os
from openai import OpenAI

# Your Ollama API key
api_key = input("Enter your Ollama API key: ").strip()

# Connect to Ollama Cloud
client = OpenAI(
    base_url="https://ollama.com/v1",
    api_key=api_key
)

print("\nTesting Ollama Cloud API...\n")

try:
    response = client.chat.completions.create(
        model="deepseek-v4.1-flash",
        messages=[
            {
                "role": "user",
                "content": "Explain Python in 3 simple sentences."
            }
        ]
    )

    print("API Connection Successful!")
    print("\nAI Response:")
    print(response.choices[0].message.content)

except Exception as e:
    print("\nAPI Connection Failed!")
    print("Error:", e)
