import argparse
from pathlib import Path

from easy_prompting.prebuilt import GPT, Prompter, PrintLogger, PrintDebugger, list_text, ListItem, ChoiceItem, pad_text, delimit_code, DataInstr, CodeInstr, ContextInstr, ListInstr, ChoiceInstr

def chat_bot(model_name: str) -> None:
    """Chat with an LM"""
    lm = GPT(model_name)
    prompter = Prompter(lm)
    prompter.set_logger(PrintLogger()) # print conversation
    prompter.set_debugger(PrintDebugger()) # get user input
    prompter.set_tag("chat bot") # set conversation tag
    prompter.set_cache(Path(f"completions/{model_name}"))
    prompter.add_message(
        "You are a ChatBot. Talk with the user.",
        role="developer"
    )
    while True:
        # 1. Wait for user input (debug mode)
        # 2. Get response from LM
        prompter.add_completion()

def programmer(model_name: str, task: str) -> None:
    """Let the LM solve a programming task"""
    lm = GPT("gpt-4o-mini", 0)
    prompter = Prompter(lm)
    prompter.set_logger(PrintLogger())
    prompter.set_debugger(PrintDebugger())
    prompter.set_cache(Path(f"completions/{model_name}"))
    prompter.set_tag("programmer")
    prompter.add_message(
        list_text(
            f"You are an autonomous agent and python expert",
            f"The user will give you a task and you should give him python code that solves the task",
            f"Do not do write any code that can be considered dangerous, unsafe, or a security risk"
        ),
        role="developer"
    )
    prompter.add_message(
        task
    )
    _, (choice, data) = prompter.get_data(
        ListInstr(
            ListItem(
                "think:",
                DataInstr(f"Think about if and how the task can be solved")
            ),
            ListItem(
                "choose:",
                ContextInstr(
                    f"Choose one of the following options",
                    ChoiceInstr(
                        ChoiceItem(
                            f"If the task is impossible",
                            f"impossible:",
                            DataInstr(f"Explain why it is impossible")
                        ),
                        ChoiceItem(
                            f"Otherwise",
                            f"possible:",
                            CodeInstr(f"Write the python code that the solves the task", "python")
                        )
                    )
                )
            )
        )
    )
    print("\nResult:")
    match choice, data:
        case "impossible:", explanation:
            print(f"The agent determined that the task is impossible to solve for the following reason:")
            print(pad_text(explanation, "  "))
            return None
        case "possible:", code:
            print(f"The agent suggest the following python code to solve the task:")
            print(pad_text(code, "  "))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="easy_prompting",
        description="Run one of the EasyPrompting demos."
    )
    parser.add_argument(
        "--demo",
        metavar="NAME",
        help="Which demo to run (default='chat bot', 'square root', 'halting problem')",
        default="chat bot"
    )
    parser.add_argument(
        "--model-name",
        metavar="NAME",
        help="The OpenAI model to use (default='gpt-4o-mini')",
        default="gpt-4o-mini"
    )
    args = parser.parse_args()
    match args.demo:
        case "chat bot":
            chat_bot(args.model_name)
        case "square root":
            # Possible task
            programmer(
                args.model_name,
                f"I need a function that calculates the square root of a whole number, if that square root is a natural number."
                f"\nIf it is not a natural number, the function can just return None."
            )
        case "halting problem":
            # Impossible task
            programmer(
                args.model_name,
                f"I need a function that determines if the code of a python function would return in finite time when executed."
            )
        case name:
            print(f"Unknown demo: \"{name}\"")