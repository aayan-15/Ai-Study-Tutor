import json
import os
import random

from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError

load_dotenv()


class GeminiService:
    """AI service using the Groq API. Class name kept so existing imports still work."""

    def __init__(self):
        api_key = os.getenv("GROK_API_KEY")

        if not api_key:
            raise RuntimeError("GROK_API_KEY not found. Add it to your .env file.")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )

        # Smartest option on your Groq account.
        # For faster replies, use "openai/gpt-oss-20b".
        self.model = "openai/gpt-oss-120b"

    # ---------------------------------------------------------
    # SHARED HELPER
    # ---------------------------------------------------------

    def _chat(self, messages, max_tokens=1000, temperature=0.2):
        """Send messages to Groq and return the reply text."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            top_p=0.8,
            # gpt-oss "thinks" before answering, and that thinking uses tokens.
            # Low effort keeps replies fast and leaves room for the answer.
            reasoning_effort="low",
            max_completion_tokens=max_tokens + 500,
        )

        return (response.choices[0].message.content or "").strip()

    def _error_message(self, e):
        """Turn API errors into friendly messages for the student."""

        if isinstance(e, AuthenticationError):
            return "The AI service rejected the API key. Please check GROK_API_KEY in your .env file."

        if isinstance(e, RateLimitError):
            return "Too many requests right now. Please wait a minute and try again."

        if isinstance(e, APIConnectionError):
            return "Couldn't reach the AI service. Please check your internet connection."

        return "Sorry, the AI service is currently unavailable. Please try again."

    # ---------------------------------------------------------
    # AI TUTOR RESPONSE
    # ---------------------------------------------------------

    def generate_response(self, message, conversation_history=None):

        try:

            system_prompt = """
You are a focused and helpful AI Study Tutor.

YOUR RESPONSIBILITIES:
1. Answer the student's current question directly.
2. Explain concepts in simple, beginner-friendly language.
3. Use examples whenever they help understanding.
4. Keep answers organized with headings and bullet points when useful.
5. For programming questions, provide correct code examples.

CONVERSATION MEMORY RULES:
1. Carefully consider previous messages before answering.
2. Understand follow-up questions using conversation context.
3. Resolve words like "it", "this", and "that" using context.
4. Stay focused on the exact topic being discussed.
5. Never introduce unrelated topics.

ANSWER LENGTH:
1. Give complete but concise answers.
2. Use approximately 100-180 words for normal explanations.
3. Do not stop in the middle of a sentence.
4. Finish with a complete sentence.

FORMATTING:
The chat window shows plain text only. Do not use Markdown symbols
like **, ##, or tables. Use simple dashes for bullet points.
"""

            messages = [{"role": "system", "content": system_prompt}]

            if conversation_history:
                messages.extend(conversation_history[-6:])

            messages.append({"role": "user", "content": message})

            answer = self._chat(messages, max_tokens=1000)

            if not answer:
                return "Sorry, I couldn't generate an answer. Please try again."

            return answer

        except Exception as e:

            print(f"Groq AI Error: {e}")
            return self._error_message(e)

    # ---------------------------------------------------------
    # PDF ANALYSIS
    # ---------------------------------------------------------

    def analyze_pdf(self, pdf_text, task, max_tokens=500):

        try:

            prompt = f"""
You are a focused AI Study Tutor.

TASK:
{task}

INSTRUCTIONS:
- Use the PDF as your primary source.
- Explain concepts in simple student-friendly language.
- Stay focused on the requested topic.
- Use simple dashes for bullet points (plain text, no Markdown symbols).
- Give a concise but complete answer.
- If the requested information is not in the PDF, clearly say so.

PDF CONTENT:
{pdf_text[:6000]}
"""

            answer = self._chat(
                [{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )

            if not answer:
                return "Sorry, I couldn't analyze this PDF. Please try again."

            return answer

        except Exception as e:

            print(f"PDF Analysis Error: {e}")
            return self._error_message(e)