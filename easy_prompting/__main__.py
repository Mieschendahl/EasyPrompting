import argparse
import sys
from easy_prompting import Prompter
from easy_prompting.prebuilt import GPT

def main():
    parser = argparse.ArgumentParser(
        description="Start an English teacher assistant using a specified OpenAI model."
    )
    parser.add_argument(
        "-m", "--model",
        default="gpt-4o-mini",
        help=(
            "The OpenAI model name to use (default: gpt-4o-mini). "
            "Common options: gpt-4o, gpt-4o-mini, gpt-4, gpt-4-turbo, gpt-3.5-turbo"
        )
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature for the model (default: 0.0)"
    )
    args = parser.parse_args()

    llm = GPT(model=args.model, temperature=args.temperature)
    prompter = Prompter(llm)\
        .set_cache_path("__cache__")\
        .set_logger(sys.stdout)\
        .set_interaction("user")\
        .add_message(
            "You are an english teacher. Please answer any questions given to you.",
            "developer"
        )

    while True:
        prompter.add_completion()

if __name__ == "__main__":
    main()
