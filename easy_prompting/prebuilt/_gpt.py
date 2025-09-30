import os
from typing import List, Optional, Any, override

from easy_prompting._llm import LLMError, LLM
from easy_prompting._message import Message

class GPT(LLM):
    _client: Optional[Any] = None

    @staticmethod
    def load_client() -> Any:
        if GPT._client is None:
            try:
                from openai import OpenAI
            except ImportError as e:
                raise LLMError("The \"openai\" library has to be manually installed to use the prebuilt GPT implementation") from e
            api_key = os.getenv("OPENAI_API_KEY", None)
            if api_key is None:
                raise LLMError("The OPENAI_API_KEY environemnt variable has to be set to a valid OpenAI API Key to use the prebuilt GPT implementation")
            GPT._client = OpenAI(api_key=api_key)

    def __init__(self, model: str = "gpt-4o-mini", temperature: int = 0, **config: Any) -> None:
        GPT.load_client()
        self.set_config(model=model, temperature=temperature, **config)

    def set_config(self, **config: Any) -> 'GPT':
        self._config = config
        return self
    
    def get_config(self) -> dict:
        return self._config

    @override
    def get_completion(self, messages: List[Message], stop: Optional[str] = None) -> str:
        openai_messages = [message.to_dict() for message in messages]
        return GPT._client.chat.completions.create( # type:ignore
                messages=openai_messages, # type:ignore
                stop=stop,
                **self._config
            ).choices[0].message.content