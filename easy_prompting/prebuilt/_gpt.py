import os
from openai import OpenAI
from easy_prompting._llm import LLM
from easy_prompting._message import Message
from typing import List, Optional, Any

class GPT(LLM):
    client: Optional[Any] = None

    @staticmethod
    def load_client() -> Any:
        if GPT.client is None:
            api_key = os.getenv("OPENAI_API_KEY", None)
            assert api_key is not None, "Missing OPENAI API KEY definition in environment"
            GPT.client = OpenAI(api_key=api_key)

    def __init__(self, model: str = "gpt-4o-mini", temperature: int = 0, **config: Any) -> None:
        GPT.load_client()
        self.set_config(model=model, temperature=temperature, **config)

    def set_config(self, **config: Any) -> 'GPT':
        self.config = config
        return self
    
    def get_config(self) -> dict:
        return self.config
    
    def get_copy(self) -> 'GPT':
        return GPT(**self.get_config())

    def get_completion(self, messages: List[Message], stop: Optional[str] = None) -> str:
        openai_messages = [message.to_dict() for message in messages]
        return GPT.client.chat.completions.create(  # type:ignore
                messages=openai_messages,  # type:ignore
                stop=stop,
                **self.config
            ).choices[0].message.content