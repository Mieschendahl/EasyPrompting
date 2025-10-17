# Setup

To set up this library, run the usual pip command:
```python
python3 -m pip install <path to this project>
```
or if you do not want to clone this project you can also run:
```python
python3 -m pip install "easy_prompting @ git+https://github.com/Mieschendahl/EasyPrompting.git"
```

After that you can import `easy_prompting` and use it in your code.

## OpenAI

If you want to use the **prebuilt** ChatGPT implementation you will have to get a valid [OpenAI API Key](https://platform.openai.com/api-keys) and set it to the environment variable `OPENAI_API_KEY`, e.g. like this in Linux:
```bash
export OPENAI_API_KEY="<your key>"
```
Vsit OpenAI's [Best Practices](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety) for more information.