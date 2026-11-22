from Core.gemini_service import GeminiService


gemini = GeminiService()

response = gemini.generate_response(
    "Hello.Who are you?"
)

print("\nGemini Response:\n")
print(response)