from abc import ABC, abstractmethod

class LLMError(Exception):
    pass

class LLM(ABC):
    @abstractmethod
    def get_completion(self, messages, stop=None):
        raise NotImplementedError("Please provide an LLM implementation to use this package.")