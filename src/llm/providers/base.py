from typing import List, Dict, Any, Optional
import base64
import json
import httpx
import asyncio


class BaseLLMProvider:
    def __init__(self, api_key: str, base_url: str, default_model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = default_model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    async def chat(
        self, messages: List[Dict[str, Any]], model: Optional[str] = None, **kwargs
    ) -> str:
        """Main async chat method that all providers should implement"""
        url = f"{self.base_url}/chat/completions"
        data = {"messages": messages, "model": model or self.default_model, **kwargs}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    async def chat_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        available_functions: Dict[str, callable],
        model: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Process conversation with tool calls."""
        # First completion with tools
        response = await self.chat(messages, model, tools=tools, **kwargs)

        # Check if we need to make tool calls
        tool_calls = kwargs.get("tool_calls", [])
        if not tool_calls:
            return response

        # Execute each tool call
        for tool_call in tool_calls:
            func_name = tool_call["function"]["name"]
            func = available_functions[func_name]

            # Parse and execute function
            args = json.loads(tool_call["function"]["arguments"])
            result = (
                await func(**args)
                if asyncio.iscoroutinefunction(func)
                else func(**args)
            )

            # Add the result to messages
            messages.append(
                {
                    "role": "tool",
                    "content": str(result),
                    "tool_call_id": tool_call["id"],
                }
            )

        # Get final response after tool execution
        return await self.chat(messages, model, tools=tools, **kwargs)
