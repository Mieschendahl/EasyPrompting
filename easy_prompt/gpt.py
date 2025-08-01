import os
from openai import OpenAI
from easy_prompt.llm import LLM

api_key = os.getenv("OPENAI_API_KEY", None)
client = OpenAI(api_key=api_key)

class GPT(LLM):
    def __init__(self, **config):
        self.set_config(**config)
        
    def set_config(self, **config):
        self.config = config
        return self
    
    def get_config(self):
        return self.config
    
    def get_copy(self):
        return GPT(**self.get_config())

    def get_completion(self, messages, stop=None):
        openai_messages = [{"role": message.role, "content": message.content} for message in messages]
        return client.chat.completions.create(
                messages=openai_messages,  # type:ignore
                stop=stop,
                **self.config
            ).choices[0].message.content

gpt_4o = GPT(model="gpt-4o", temperature=0)
gpt_4o_mini = GPT(model="gpt-4o-mini", temperature=0)