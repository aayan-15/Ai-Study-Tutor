
import ollama
import time

print("Testing Local Ollama AI...")
print("Model: qwen2.5:0.5b\n")

try:
    start_time = time.time()

    response = ollama.chat(
        model="qwen2.5:0.5b",
        messages=[
            {
                "role": "user",
                "content": "Explain Python functions with a simple example."
            }
        ],
        options={
            "temperature": 0.4,
            "num_predict": 200,
            "num_ctx": 2048
        }
    )

    elapsed_time = time.time() - start_time

    print("AI Connection Successful!\n")
    print("AI Response:")
    print(response["message"]["content"])

    print(f"\nResponse Time: {elapsed_time:.2f} seconds")

except Exception as e:
    print("\nAI Connection Failed!")
    print("Error:", e)
