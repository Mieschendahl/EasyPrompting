# Setup

To set up this library, run the usual pip command:
```bash
python3 -m pip install <path to this project>
```

If you do not want to clone this project you can also run:
```bash
python3 -m pip install "easy_prompting @ git+https://github.com/Mieschendahl/EasyPrompting.git"
```

After that you can import `easy_prompting` and use it in your code.

If you want to execute the demo code run:
```bash
python3 -m easy_prompting -h
```

## OpenAI

If you want to use the **prebuilt** ChatGPT implementation you will have to get a valid [OpenAI API Key](https://platform.openai.com/api-keys) and set it to the environment variable `OPENAI_API_KEY`.

For example, like this in Linux:
```bash
export OPENAI_API_KEY="<your key>"
```
Vsit OpenAI's [Best Practices](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety) for more information.

After that install the `openai` library:
```bash
python3 -m pip install openai
```

Then you are ready to setup `easy_prompting` in the usual way.