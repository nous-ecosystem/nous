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
        max_tokens: int = 8000,
        temperature: float = 0.85,
    ) -> str:
        """Generate a response using the Groq API."""
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False,
                top_p=0.9,
                presence_penalty=0.6,
                frequency_penalty=0.7,
            )

            # More detailed response validation
            if not response or not response.choices:
                print("Error: Empty response from Groq API")
                return "I'm having trouble connecting to my language model. Please try again."

            content = response.choices[0].message.content
            if not content or not content.strip():
                print("Error: Empty content in response")
                return (
                    "I apologize, but I received an empty response. Please try again."
                )

            return content

        except Exception as e:
            print(f"Detailed error in generate_response: {type(e).__name__}: {str(e)}")
            return "I'm having technical difficulties right now. Please try again in a moment."
