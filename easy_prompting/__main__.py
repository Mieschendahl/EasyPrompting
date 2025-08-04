import sys
from easy_prompting import Prompter
from easy_prompting.prebuilt import GPT

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 1:
        print("Expecting arguments: <openai model name e.g. gpt-4o-mini>")
        exit(0)

    llm = GPT(model=args[0], temperature=0)
    p = Prompter(llm)\
        .set_logger(sys.stdout)\
        .set_interaction(True)\
        .add_message("You are an english teacher. Please answer any questions given to you.", "developer")

    while True:
        p.add_completion()