import json
import random

import ollama


class GeminiService:
    """Local AI service (Ollama). Class name kept so existing imports still work."""

    def __init__(self):
        # 0.5b is very weak at structured output. If quizzes still fail often,
        # try "qwen2.5:3b", "llama3.2:3b" or "qwen2.5:7b".
        self.model = "qwen2.5:0.5b"

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
"""

            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ]

            if conversation_history:
                messages.extend(conversation_history[-6:])

            messages.append({
                "role": "user",
                "content": message
            })

            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": 0.2,
                    "num_predict": 1000,
                    "num_ctx": 4096,
                    "top_p": 0.8
                },
                keep_alive="10m"
            )

            answer = response["message"]["content"].strip()

            if not answer:
                return "Sorry, I couldn't generate an answer. Please try again."

            return answer

        except Exception as e:

            print(f"Local AI Error: {e}")

            return (
                "Sorry, the AI service is currently unavailable. "
                "Please check whether Ollama is running."
            )

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
- Use headings and bullet points when useful.
- Give a concise but complete answer.
- If the requested information is not in the PDF, clearly say so.

PDF CONTENT:
{pdf_text[:6000]}
"""

            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0.2,
                    "num_predict": max_tokens,
                    # 6000 characters is roughly 1500 tokens, plus the reply.
                    # 2048 would truncate the prompt.
                    "num_ctx": 4096,
                    "top_p": 0.8
                },
                keep_alive="10m"
            )

            answer = response["message"]["content"].strip()

            if not answer:
                return "Sorry, I couldn't analyze this PDF. Please try again."

            return answer

        except Exception as e:

            print(f"PDF Analysis Error: {e}")

            return "Sorry, I couldn't analyze this PDF. Please try again."

    