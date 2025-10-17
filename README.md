# EasyPrompting

EasyPrompting is a Python library for simplifying language model (LM) interactions.

## Features

Prompting LMs usually entails a couple of challenges:
- Supporting different kinds of LM APIs
- Logging and debugging interactions
- Caching LM responses to save on time and cost
- Having persistant memory over longer interactions
- Getting responses in a specified format from the LM

## Demos

`easy_prompting/__main__.py` demonstrates simple use cases for this library which can be tested after following the setup instructions in `SETUP.md`.

## Manual

EasyPrompting provides two main entry points:
- `easy_prompting` which contains the core architecture
- `easy_prompting.prebuilt` which contains additional auxilary architecture for ease of use in common use cases

### Core Architecture

The core architecture focuses on the `prompter` class. It handles the interaction with the LM, as well as the caching of LLM respones.

The `LM` class provides an abstract interface to any LM implementation.

The `Logger` class provides an abstract interface for logging and printing conversations between the `prompter` and an `LM`.

The `Interaction` class provides an abstract interface for interacting with the LM in conversations for debugging and chatting purposes.

The `Instruction` class provides an abstract interface for instructing the `LM` on how it should format responses, and how to extract relevant information from those responses.

### Auxilary Architecture

The auxilary architecture mainly provides implementations of the core architecture interfaces for common use cases, as well as some utilities.