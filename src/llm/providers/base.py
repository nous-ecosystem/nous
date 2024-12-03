from typing import List, Dict, Any, Optional
import base64
import json
import httpx


class BaseLLMProvider:
    def __init__(self, api_key: str, base_url: str, default_model: str):
        """Generic LLM provider initialization."""
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = default_model

    def _get_headers(self) -> Dict[str, str]:
        """Standard headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _encode_image(self, image_path: str) -> str:
        """Encode an image to base64."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def create_completion(
        self, messages: List[Dict[str, Any]], model: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Generic synchronous completion method."""
        url = f"{self.base_url}/chat/completions"
        data = {"messages": messages, "model": model or self.default_model, **kwargs}

        with httpx.Client() as client:
            response = client.post(url, headers=self._get_headers(), json=data)
            response.raise_for_status()
            return response.json()

    async def create_completion_async(
        self, messages: List[Dict[str, Any]], model: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Generic asynchronous completion method."""
        url = f"{self.base_url}/chat/completions"
        data = {"messages": messages, "model": model or self.default_model, **kwargs}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self._get_headers(), json=data)
            response.raise_for_status()
            return response.json()

    def process_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        available_functions: Dict[str, callable],
    ) -> str:
        """Process conversation with tool calls."""
        response = self.create_completion(messages, tools=tools)
        tool_calls = (
            response.get("choices", [{}])[0].get("message", {}).get("tool_calls", [])
        )

        if not tool_calls:
            return response["choices"][0]["message"]["content"]

        # Execute tool calls
        for tool_call in tool_calls:
            func_name = tool_call["function"]["name"]
            func = available_functions[func_name]

            # Parse arguments safely
            args = tool_call["function"]["arguments"]
            args = json.loads(args) if isinstance(args, str) else args

            # Call function and add response
            result = func(**args)
            messages.append(
                {
                    "role": "tool",
                    "content": str(result),
                    "tool_call_id": tool_call["id"],
                }
            )

        # Get final response
        final_response = self.create_completion(messages, tools=tools)
        return final_response["choices"][0]["message"]["content"]
