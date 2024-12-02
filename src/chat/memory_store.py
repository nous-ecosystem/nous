from typing import Dict, List, Optional
import lancedb
from datetime import datetime
from dataclasses import dataclass
from openai import OpenAI
from src.core.config import config
from .groq_client import GroqClient
import json


@dataclass
class MemoryEntry:
    content: str
    summary: str
    sentiment: float
    keywords: List[str]
    user_id: str
    username: str
    timestamp: datetime
    channel_id: int
    vector: List[float]


class MemoryStore:
    def __init__(self, db_path: str = "./.lancedb"):
        self.db = lancedb.connect(db_path)
        self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.groq_client = GroqClient(config.GROQ_API_KEY)
        self.table = self._init_table()

    def _init_table(self):
        """Initialize or get the memory table"""
        try:
            return self.db.open_table("chat_memories")
        except:
            # Create new table with schema
            return self.db.create_table(
                "chat_memories",
                data=[
                    {
                        "content": "",
                        "summary": "",
                        "sentiment": 0.0,
                        "keywords": [],
                        "user_id": "",
                        "username": "",
                        "timestamp": datetime.now(),
                        "channel_id": 0,
                        "vector": [0.0] * 1536,  # OpenAI embedding dimension
                    }
                ],
            )

    def _get_embedding(self, text: str) -> List[float]:
        """Get OpenAI embedding for text"""
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-small", input=text
        )
        return response.data[0].embedding

    def _analyze_conversation(self, conversation: str) -> Dict:
        """Analyze conversation using Groq with prefilled format"""
        prompt = """Analyze the following conversation and provide:
1. A brief summary (1-2 sentences)
2. A sentiment score (-1.0 to 1.0, where -1 is very negative, 0 is neutral, and 1 is very positive)
3. A list of 3-5 key topics or themes

Conversation:
{conversation}

Provide the analysis in the exact JSON format shown below."""

        messages = [
            {"role": "system", "content": "You are a conversation analyzer."},
            {"role": "user", "content": prompt.format(conversation=conversation)},
            {
                "role": "assistant",
                "content": """```json
{
    "summary": "",
    "sentiment": 0.0,
    "keywords": []
}""",
            },
        ]

        try:
            completion = self.groq_client.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent formatting
                stop=["```"],  # Stop at the end of the JSON block
            )

            # Collect the response
            json_str = ""
            for chunk in completion:
                json_str += chunk.choices[0].delta.content or ""

            # Clean up and parse JSON
            json_str = json_str.strip()
            if not json_str.endswith("}"):
                json_str += "}"
            analysis = json.loads(json_str)

            return {
                "summary": analysis["summary"],
                "sentiment": float(analysis["sentiment"]),
                "keywords": analysis["keywords"],
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing analysis response: {e}")
            # Fallback values
            return {
                "summary": "Error analyzing conversation",
                "sentiment": 0.0,
                "keywords": [],
            }
        except Exception as e:
            print(f"Error in conversation analysis: {e}")
            return {
                "summary": "Error analyzing conversation",
                "sentiment": 0.0,
                "keywords": [],
            }

    def store_memory(
        self, content: str, user_id: str, username: str, channel_id: int
    ) -> None:
        """Store a new memory entry"""
        analysis = self._analyze_conversation(content)
        vector = self._get_embedding(content)

        entry = {
            "content": content,
            "summary": analysis["summary"],
            "sentiment": analysis["sentiment"],
            "keywords": analysis["keywords"],
            "user_id": user_id,
            "username": username,
            "timestamp": datetime.now(),
            "channel_id": channel_id,
            "vector": vector,
        }

        self.table.add([entry])

    def search_memories(
        self,
        query: str,
        limit: int = 5,
        user_id: Optional[str] = None,
        channel_id: Optional[int] = None,
    ) -> List[Dict]:
        """Search memories by similarity and optional filters"""
        query_vector = self._get_embedding(query)
        search_query = self.table.search(query_vector)

        if user_id:
            search_query = search_query.where(f"user_id = '{user_id}'")
        if channel_id:
            search_query = search_query.where(f"channel_id = {channel_id}")

        return search_query.limit(limit).to_list()
