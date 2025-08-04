import os
from openai import OpenAI
from easy_prompting._llm import LLM
from easy_prompting._message import Message
from typing import List, Optional, Any

api_key: Optional[str] = os.getenv("OPENAI_API_KEY", None)
client = OpenAI(api_key=api_key)

class GPT(LLM):
    def __init__(self, **config: Any) -> None:
        self.set_config(**config)
        
    def set_config(self, **config: Any) -> 'GPT':
        self.config = config
        return self
    
    def get_config(self) -> dict:
        return self.config
    
    def get_copy(self) -> 'GPT':
        return GPT(**self.get_config())

    def get_completion(self, messages: List[Message], stop: Optional[str] = None) -> str:
        openai_messages = [{"role": message.role, "content": message.content} for message in messages]
        return client.chat.completions.create(
                messages=openai_messages,  # type:ignore
                stop=stop,
                **self.config
            ).choices[0].message.content

gpt_4o = GPT(model="gpt-4o", temperature=0)
gpt_4o_mini = GPT(model="gpt-4o-mini", temperature=0)