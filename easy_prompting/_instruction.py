from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, override

from easy_prompting._utils import enumerate_text, pad_text, scope_text, wrap_text

class ExtractionError(Exception):
    pass

class Instruction(ABC):
    @abstractmethod
    def describe(self) -> str:
        pass

    @abstractmethod
    def extract(self, data: str) -> Any:
        pass

@dataclass
class IItem:
    key: str
    value: Optional[Instruction] = None

class IList(Instruction):
    stop = "stop"

    def __init__(self, context: str, *items: IItem, effect: Optional[str] = None):
        assert len(items) > 0, "Need at least one item in a List"
        self._context = context
        self._items = list(items)
        self._effect = effect
    
    @override
    def describe(self) -> str:
        items = []
        for item in self._items:
            items.append(f"Write \"{wrap_text(item.key)}\"")
            if item.value is not None:
                items.append(item.value.describe())
        effect = ""
        if self._effect is not None:
            if len(items) > 0:
                effect += "\n"
            effect += f"-> {pad_text(self._effect, pad_first=False)}"
        return self._context + scope_text(enumerate_text(*items) + effect)

    @override
    def extract(self, data: str) -> list[Any]:
        extraction = []
        for item in self._items:
            key = wrap_text(item.key)
            if key not in data:
                raise ExtractionError(f"List extraction failed: missing key {key!r} in {data!r}")
            head, data = data.split(key, 1)
            extraction.append(head)
        extraction = extraction[1:] + [data]
        extraction_out = []
        for i, item in enumerate(self._items):
            extraction_out.append(extraction[i] if item.value is None else item.value.extract(extraction[i]))
        return extraction_out