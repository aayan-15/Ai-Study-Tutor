
import ollama


class GeminiService:

    def __init__(self):
        self.model = "qwen2.5:0.5b"

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
2. Understand follow-up questions such as "give me an example",
   "explain it", and "what about the second one".
3. Resolve words like "it", "this", and "that" using conversation context.
4. Stay focused on the exact topic being discussed.
5. Never introduce unrelated topics.
6. Do not explain tuples, sets, dictionaries, or other concepts
   unless the student asks about them or they are directly relevant.

ANSWER LENGTH:
1. Give complete but concise answers.
2. Use approximately 100-180 words for normal explanations.
3. Do not stop in the middle of a sentence.
4. Finish your explanation with a complete sentence.
5. Do not repeat the same information unnecessarily.
"""

            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ]

            # Include only the most recent 6 conversation messages
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
                    "num_predict": 1500,
                    "num_ctx": 2048,
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


    def analyze_pdf(self, pdf_text, task):

        try:

            prompt = f"""
You are an AI Study Tutor.

The student has uploaded a PDF containing study material.

Your task:
{task}

Instructions:
- Use only the information provided in the PDF.
- Explain everything in simple student-friendly language.
- Organize the answer using headings and bullet points.
- Do not introduce unrelated topics.
- If the requested information is not present in the PDF,
  clearly say so.

PDF CONTENT:
{pdf_text[:12000]}
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
                    "num_predict": 1500,
                    "num_ctx": 2048
                },
                keep_alive="10m"
            )

            return response["message"]["content"].strip()

        except Exception as e:

            print(f"PDF Analysis Error: {e}")

            return "Sorry, I couldn't analyze this PDF. Please try again."

