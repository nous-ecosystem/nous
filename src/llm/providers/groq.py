from groq import AsyncGroq
import base64
from src.config import Config  # Import the Config class


class GroqProvider:
    def __init__(self):
        config = Config()  # Create an instance of Config
        self.client = AsyncGroq(api_key=config.groq_api_key)

    async def chat_completion(
        self,
        messages,
        model="llama3-8b-8192",
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
    ):
        chat_completion = await self.client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stop=None,
            stream=False,
        )
        return chat_completion.choices[0].message.content

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def image_chat_completion(self, image_path, user_message):
        base64_image = self.encode_image(image_path)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_message},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ]
        return self.client.chat.completions.create(
            messages=messages, model="llama-3.2-11b-vision-preview"
        )

    async def moderate_content(self, user_message):
        response = await self.client.chat.completions.create(
            messages=[{"role": "user", "content": user_message}],
            model="llama-guard-3-8b",
        )
        return response.choices[0].message.content
