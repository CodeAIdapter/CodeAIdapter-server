import openai
from config import Config
from .base import LLMBase

class OpenAIChat(LLMBase):
    _initialized = False
    _client = None
    DEFAULT_MODEL = "gpt-4o-mini-2024-07-18"

    @classmethod
    def _initialize(cls):
        if not cls._initialized:
            cls._client = openai.OpenAI()
            cls._initialized = True

    @classmethod
    def chat(cls, dev_prompt:str, usr_prompt: str, model: str = None) -> str:
        cls._initialize()
        model_name = model or cls.DEFAULT_MODEL
        response = cls._client.chat.completions.create(
            model = model_name,
            store = True,
            messages = [
                {"role": "developer", "content": dev_prompt},
                {"role": "user", "content": usr_prompt}
            ]
        )
        return response.choices[0].message.content

        