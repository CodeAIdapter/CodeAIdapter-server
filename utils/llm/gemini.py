import vertexai
from google.cloud import aiplatform
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel

from config import Config
from .base import LLMBase

class GeminiChat(LLMBase):
    _initialized = False
    _models = {}
    DEFAULT_MODEL = "gemini-2.0-pro-exp-02-05"

    @classmethod
    def _initialize(cls, model_name: str = None):
        model_name = model_name or cls.DEFAULT_MODEL
        if not cls._initialized or model_name not in cls._models:
            if not cls._initialized:
                credentials = service_account.Credentials.from_service_account_file(Config.GCP_CREDENTIALS)
                vertexai.init(project=Config.GCP_PROJECT_ID, location="us-central1")
                aiplatform.init(project=Config.GCP_PROJECT_ID, location="us-central1", credentials=credentials)
                cls._initialized = True
            cls._models[model_name] = GenerativeModel(model_name)

    @classmethod
    def chat(cls, prompt: str, model: str = None) -> str:
        model_name = model or cls.DEFAULT_MODEL
        cls._initialize(model_name)
        response = cls._models[model_name].generate_content(prompt)
        return response.text