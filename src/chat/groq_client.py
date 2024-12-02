import os
from typing import List, Dict, Optional
from groq import Groq


class GroqClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

        if not self.api_key:
            raise ValueError(
                "Groq API key must be provided or set in GROQ_API_KEY environment variable"
            )

        key_preview = (
            f"{self.api_key[:4]}...{self.api_key[-4:]}" if self.api_key else "None"
        )
        print(f"Initializing Groq client with API key: {key_preview}")

        try:
            self.client = Groq(api_key=self.api_key)
        except Exception as e:
            print(f"Groq client initialization error: {e}")
            raise

        self.model = "llama-3.1-70b-versatile"

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> str:
        """Generate a response using the Groq API."""
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False,
            )

            # Ensure we always return a string
            content = response.choices[0].message.content
            return content if content else "I couldn't generate a meaningful response."

        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again later."
