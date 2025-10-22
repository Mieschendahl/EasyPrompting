import argparse

from easy_prompting.prebuilt import GPT, Prompter, PrintLogger, PrintDebugger, list_text, pad_text, delimit_code, Item, ListI, TextI, CodeI, ChoiceI

def chat_bot() -> None:
    """Chat with an LM"""
    lm = GPT("gpt-4o-mini")
    prompter = Prompter(lm)
    prompter.set_logger(PrintLogger()) # print conversation
    prompter.set_debugger(PrintDebugger()) # get user input
    prompter.set_tag("chat bot") # set conversation tag
    prompter.set_cache("completions")
    prompter.add_message(
        "You are a ChatBot. Talk with the user.",
        role="developer"
    )
    while True:
        # 1. Wait for user input (debug mode)
        # 2. Get response from LM
        prompter.add_completion()

def programmer(task: str) -> None:
    """Let the LM solve a programming task"""
    lm = GPT("gpt-4o-mini", 0)
    prompter = Prompter(lm)
    prompter.set_logger(PrintLogger())
    prompter.set_debugger(PrintDebugger())
    prompter.set_cache("completions")
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
    (choice, data) = prompter.get_data(
        ListI(
            f"Do the following",
            Item(
                "think",
                TextI(f"Think about if and how the task can be solved")
            ),
            Item(
                "choose",
                ChoiceI(
                    f"Choose one of the following options",
                    ListI(
                        f"If the task is impossible to achieve",
                        Item(
                            "impossible",
                            TextI(f"Explain why it is impossible")
                        )
                    ),
                    ListI(
                        f"Otherwise",
                        Item(
                            "python",
                            CodeI(f"Write the python code that the solves the task", "python")
                        )
                    )
                )
            ),
            add_stop=True
        )
    )[1]
    match choice, data[0]:
        case "impossible", explanation:
            print(f"The agent determined that the task is impossible to solve for the following reason:")
            print(pad_text(explanation, "  "))
            return None
        case "python", code:
            print(f"The agent suggest the following python code to solve the task:")
            print(pad_text(delimit_code(code, "python"), "  "))

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
    args = parser.parse_args()
    match args.demo:
        case "chat bot":
            chat_bot()
        case "square root":
            # Possible task
            programmer(
                f"I need a function that calculates the square root of a whole number, if that square root is a natural number."
                f"\nIf it is not a natural number, the function can just return None."
            )
        case "halting problem":
            # Impossible task
            programmer(
                f"I need a function that determines if the code of a python function would return in finite time when executed."
            )
        case name:
            print(f"Unknown demo: \"{name}\"")