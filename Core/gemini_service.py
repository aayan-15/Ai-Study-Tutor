import os
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()


class GeminiService:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Check your .env file."
            )

        self.client = genai.Client(api_key=api_key)

        self.model = "gemini-4-hydrogen"

    def generate_response(self, prompt):

        try:

            start_time = time.time()

            response = self.client.interactions.create(
                model=self.model,
                input=prompt
            )

            end_time = time.time()

            print(
                f"Gemini response time: "
                f"{end_time - start_time:.2f} seconds"
            )

            return response.output_text

        except Exception as error:

            print("Gemini API Error:", error)

            return (
                "Sorry, I couldn't generate a response. "
                "Please check your internet connection or API configuration."
            )