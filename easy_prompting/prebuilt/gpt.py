import os
from typing import List, Optional, Any, override

from easy_prompting.lm import LMError, LM
from easy_prompting.message import Message

class GPT(LM):
    _client: Any = None

    @staticmethod
    def load_client() -> Any:
        if GPT._client is None:
            try:
                from openai import OpenAI
            except ImportError as e:
                raise LMError("The \"openai\" library has to be manually installed to use the prebuilt GPT implementation") from e
            api_key = os.getenv("OPENAI_API_KEY", None)
            if api_key is None:
                raise LMError("The OPENAI_API_KEY environemnt variable has to be set to a valid OpenAI API Key to use the prebuilt GPT implementation")
            GPT._client = OpenAI(api_key=api_key)

    def __init__(self, model_name: str = "gpt-4o-mini"):
        GPT.load_client()
        self._model_name = model_name
        self.set_config()

    def set_config(self, **config: Any) -> 'GPT':
        self._config = config
        return self
    
    def get_config(self) -> dict[str, Any]:
        return self._config

    @override
    def get_completion(self, messages: List[Message], stop: Optional[str] = None) -> str:
        openai_messages = [message.to_dict() for message in messages]
        return GPT._client.chat.completions.create(
                messages=openai_messages,
                stop=stop,
                model=self._model_name,
                **self._config
            ).choices[0].message.content