from dataclasses import dataclass
from typing import Any, Callable, Optional, override

from easy_prompting.instruction import ExtractionError, Instruction
from easy_prompting.utils import scope_text, enumerate_text, list_text, wrap_text

def extract_code(code: str, language: str = "") -> str:
    lines = code.split("\n")
    start = None
    for i, line in enumerate(lines):
        if line.startswith("```" + language):
            start = i + 1
            break
    if start is not None:
        for i, line in enumerate(lines[start:]):
            if line.startswith("```"):
                return "\n".join(lines[start:start+i]).strip()
    return "\n".join(line for line in lines if not line.startswith("```")).strip()

def delimit_code(text: str, keyword: str = "") -> str:
    return f"```{keyword}\n{text}\n```"

class DataI(Instruction):
    def __init__(self, text: str, extractor: Callable[[str], Any] = lambda x: x.strip()):
        self._text = text
        self._extractor = extractor
    
    @override
    def describe(self) -> str:
        return self._text

    @override
    def extract(self, data: str) -> Any:
        return self._extractor(data)

class CodeI(DataI):
    @override
    def __init__(self, text: str, language: str = ""):
        super().__init__(text, extract_code)
        self._language = language

    @override
    def describe(self) -> str:
        return (
            f"Do the following"
            + enumerate_text(
                f"Write \"```{self._language}\"",
                self._text,
                f"Write \"```\"",
                add_scope=True
            )
        )

class ContextI(Instruction):
    def __init__(self, pre: str, instruction: Instruction, post: Optional[str] = None):
        self._pre = pre
        self._instruction = instruction
        self._post = post
    
    @override
    def describe(self) -> str:
        return (
            self._pre
            + scope_text(self._instruction.describe())
            + ("" if self._post is None else f"\n{self._post}")
        )
    
    @override
    def extract(self, data: str, depth: int = 0) -> list[Any]:
        return self._instruction.extract(data)

@dataclass
class ListItem:
    def __init__(self, key: str, instruction: Instruction):
        self._key = key
        self._instruction = instruction

class ListI(Instruction):
    def __init__(self, *items: ListItem):
        self._items = items
    
    @override
    def describe(self) -> str:
        descriptions: list[str] = []
        for item in self._items:
            descriptions.append(f"Write \"{item._key}\"")
            descriptions.append(item._instruction.describe())
        return enumerate_text(*descriptions)

    @override
    def extract(self, data: str) -> list[Any]:
        _data = data
        sub_data: list[str] = []
        for item in self._items:
            if item._key not in data:
                raise ExtractionError(f"Enumerate extraction failed: key {item._key!r} missing in data {_data!r}")
            head, data = data.split(item._key, 1)
            sub_data.append(head)
        sub_data = sub_data[1:] + [data]
        extractions = []
        for _sub_data, item in zip(sub_data, self._items):
            extractions.append(item._instruction.extract(_sub_data))
        return extractions

@dataclass
class ChoiceOption:
    def __init__(self, condition: str, key: str, instruction: Instruction):
        self._condition = condition
        self._key = key
        self._instruction = instruction

class ChoiceI(Instruction):
    def __init__(self, *options: ChoiceOption):
        self._options = options
    
    @override
    def describe(self) -> str:
        descriptions: list[str] = []
        for option in self._options:
            descriptions.append(
                option._condition
                + enumerate_text(
                    f"Write \"{option._key}\"",
                    option._instruction.describe(),
                    add_scope=True
                )
            )
        return list_text(*descriptions)

    @override
    def extract(self, data: str) -> tuple[str, Any]:
        for option in self._options:
            if option._key in data:
                sub_data = data.split(option._key, 1)[1]
                return option._key, option._instruction.extract(sub_data)
        keys = [option._key for option in self._options]
        raise ExtractionError(f"List extraction failed: no valid option key {keys!r} found in data {data!r}")