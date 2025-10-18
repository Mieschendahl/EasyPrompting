# EasyPrompting

EasyPrompting is a Python library for simplifying language model (LM) interactions.

## Features

Prompting LMs usually entails a couple of challenges:
- Supporting different kinds of LM APIs
- Logging and debugging interactions
- Caching LM responses to save on time and cost
- Having persistant memory over longer interactions
- Getting responses in a specified format from the LM

## Demo
Here is how to make a simple chat bot using the logger and debugger features:
```python
from easy_prompting.prebuilt import *

def chat_bot() -> None:
    prompter = Prompter(GPT())
    prompter.set_logger(PrintLogger())
    prompter.set_debugger(PrintDebugger())
    prompter.add_message(
        "You are a ChatBot. Talk with the user.",
        role="developer"
    )
    while True:
        # 1. Wait for user input (debug mode)
        # 2. Get response from LM
        prompter.add_completion()
```
Shell output:
```bash
Message(tag=None, role='developer', idx=0):
  You are a ChatBot. Talk with the user.

Input(role='user', continue='↵', exit='Ctrl+c'):
  Hi :) # Waited for user input

Message(tag=None, role='user', idx=1):
  Hi :) # Send user input to LM

Message(tag=None, role='assistant', idx=2):
  Hello! 😊 How can I assist you today?
```

`easy_prompting/__main__.py` demonstrates simple use cases for this library, which can also be tested after following the setup instructions in `SETUP.md`.

## Manual

EasyPrompting provides two main entry points:
- `easy_prompting` which contains the core architecture
- `easy_prompting.prebuilt` which contains additional auxilary architecture for convinience in common use cases

### Core Architecture

The core architecture focuses on the `prompter` class. It handles the interaction with the LM, as well as the caching of LM respones.

The `LM` class provides an abstract interface to any LM implementation.

The `Logger` class provides an abstract interface for logging and printing conversations between the `prompter` and the `LM`.

The `Debugger` class provides an abstract interface for interacting with the `LM` in conversations for debugging purposes.

The `Instruction` class provides an abstract interface for instructing the `LM` on how it should format responses, and how to extract relevant information from those responses.

### Auxilary Architecture

The auxilary architecture mainly provides implementations of the core architecture interfaces for common use cases, as well as some utilities.