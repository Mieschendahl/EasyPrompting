import argparse
from easy_prompting.prebuilt import Prompter, GPT, LogPrint, PrintInteraction, list_text, pad_text, delimit_code, IList, IItem, IText, ICode, IChoice

def chat_bot() -> None:
    lm = GPT("gpt-4o-mini", 0)
    prompter = Prompter(lm)
    prompter.set_logger(LogPrint())
    prompter.set_interaction(PrintInteraction())
    prompter.set_cache_path("completions")
    prompter.set_tag("chat bot")
    prompter.add_message(
        "You are a ChatBot and should talk with the user",
        role="developer"
    )
    while True:
        prompter.add_completion()

def python_agent(task: str) -> None:
    lm = GPT("gpt-4o-mini", 0)
    agent = Prompter(lm)
    agent.set_logger(LogPrint())
    agent.set_interaction(PrintInteraction())
    agent.set_cache_path("completions")
    agent.set_tag("shell agent")
    agent.add_message(
        list_text(
            f"You are an autonomous agent and python expert",
            f"The user will give you a task and you should give him python code that solves the task",
            f"Do not do write any code that can be considered dangerous, unsafe, or a security risk"
        ),
        role="developer"
    )
    agent.add_message(
        task
    )
    (choice, data) = agent.get_data(
        IList(
            f"Do the following",
            IItem(
                "think",
                IText(f"Think about if and how the task can be solved")
            ),
            IItem(
                "choose",
                IChoice(
                    f"Choose one of the following options",
                    IList(
                        f"If the task is impossible to achieve",
                        IItem(
                            "impossible",
                            IText(f"Explain why it is impossible")
                        )
                    ),
                    IList(
                        f"Otherwise",
                        IItem(
                            "python",
                            ICode(f"Write the python code that the solves the task", "python")
                        )
                    )
                )
            )
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
        prog="python3 -m easy_prompting",
        description="Run one of the EasyPrompting demos."
    )
    parser.add_argument("demo", help="Which demo to run: 'chat' or 'python'")
    args = parser.parse_args()

    match args.demo:
        case "chat":
            chat_bot()
        case "python":
            # Possible task
            python_agent(
                f"I need a function that calculates the square root of a whole number, if that square root is a natural number."
                f"\nIf it is not a natural number, the function can just return None."
            )
            # Impossible task
            # python_agent(
            #     f"I need a function that determines if the code of a python function would return in finite time when executed."
            # )
        case _:
            print("Unknown demo")