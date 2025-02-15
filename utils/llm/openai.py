import openai
from config import Config
from .base import LLMBase

class OpenAIChat(LLMBase):
    """
    A class to interact with OpenAI's chat models.

    Attributes:
        _initialized (bool): Indicates if the OpenAI client has been initialized.
        _client (openai.OpenAI): The OpenAI client instance.
        DEFAULT_MODEL (str): The default model to use for chat completions.
    """
    _initialized = False
    _client = None
    DEFAULT_MODEL = "gpt-4o-mini-2024-07-18"

    @classmethod
    def _initialize(cls):
        """
        Initialize the OpenAI client with the provided API key.
        """
        if not cls._initialized:
            cls._client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            cls._initialized = True

    @classmethod
    def chat(cls, dev_prompt: str, usr_prompt: str, model: str = None) -> str:
        """
        Generate a chat completion response from the OpenAI model.

        Args:
            dev_prompt (str): The developer's prompt message.
            usr_prompt (str): The user's prompt message.
            model (str, optional): The model to use for chat completions. Defaults to None.

        Returns:
            str: The content of the chat completion response.
        """
        cls._initialize()
        model_name = model or cls.DEFAULT_MODEL
        response = cls._client.chat.completions.create(
            model=model_name,
            store=True,
            messages=[
                {"role": "developer", "content": dev_prompt},
                {"role": "user", "content": usr_prompt}
            ]
        )
        return response.choices[0].message.content
