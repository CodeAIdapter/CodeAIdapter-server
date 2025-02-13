from abc import ABC, abstractmethod

class LLMBase(ABC):
    @abstractmethod
    def chat(self, prompt: str) -> str:
        pass