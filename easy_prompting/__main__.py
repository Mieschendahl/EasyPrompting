from easy_prompting.prebuilt import Prompter, GPT, LogPrint, PrintInteraction

def main(model_name: str, temperature: int, cache_path: str):
    prompter = Prompter(GPT(model=model_name, temperature=temperature))
    prompter.set_logger(LogPrint())
    prompter.set_interaction(PrintInteraction())
    prompter.set_cache_path(cache_path)
    prompter.set_tag("example")
    prompter.add_message(
        "You are a ChatBot and should talk with the user",
        role="developer"
    )
    while True:
        prompter.add_completion()

if __name__ == "__main__":
    main(model_name="gpt-4o-mini", temperature=0, cache_path="completions")