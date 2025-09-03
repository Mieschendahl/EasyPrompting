import argparse
import sys
from easy_prompting import Prompter
from easy_prompting.prebuilt import GPT, FormatLogger

def run_from_commandline(model_name: str, temperature: int, interactive: bool, cache_path: str):
    prompter = Prompter(GPT(model=model_name, temperature=temperature))\
        .set_loggers(FormatLogger(sys.stdout))\
        .set_cache_path(cache_path)\
        .set_interaction("user" if interactive else None)\
        .add_message(
            "You are a ChatBot and should talk with the user",
            role="developer"
        )

    while True:
        prompter.add_completion()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Interact with ChatGPT."
    )
    parser.add_argument(
        "--model-name",
        default="gpt-4o-mini",
        metavar="NAME",
        help=("OpenAI model to use (i.g. gpt-4o, gpt-4o-mini, gpt-4, gpt-4-turbo, gpt-3.5-turbo) (default: gpt-4o-mini).")
    )
    parser.add_argument(
        "--temperature",
        type=int,
        default=0,
        metavar="VALUE",
        help=(
            "The temperature that the model should use for completion generation (default: 0)"
        )
    )
    parser.add_argument(
        "--cache-path",
        metavar="PATH",
        default="./completions",
        help="Cache LLM responses in PATH (default: ./completions)"
    )
    args = parser.parse_args()
    run_from_commandline(
        model_name=args.model_name,
        temperature=args.temperature,
        interactive=True,
        cache_path=args.cache_path
    )