from openai import OpenAI
import base64
from src.config import Config


class OpenAIProvider:
    def __init__(self):
        config = Config()
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    def chat_completion(self, messages, model="gpt-4o-mini", max_tokens=300):
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
        )
        return response.choices[0]

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
        return self.client.chat.completions.create(messages=messages)

    def create_embedding(self, input_text, model="text-embedding-3-small"):
        response = self.client.embeddings.create(input=input_text, model=model)
        return response.data[0].embedding

    def moderate_content(self, content):
        response = self.client.moderations.create(
            model="omni-moderation-latest", input=content
        )
        return response
