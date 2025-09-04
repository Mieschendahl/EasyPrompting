def delimit_code(text: str, keyword: str = "") -> str:
    return f"```{keyword}\n{text}\n```"