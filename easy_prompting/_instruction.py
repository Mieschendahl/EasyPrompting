from abc import ABC, abstractmethod
from typing import Any, Optional, override

from easy_prompting._utils import enumerate_text, wrap_text

class ExtractionError(Exception):
    pass

class Instruction(ABC):
    @abstractmethod
    def describe(self) -> str:
        pass

    @abstractmethod
    def extract(self, data: str) -> Any:
        pass

class IItem:
    def __init__(self, key: str, value: Optional[Instruction] = None):
        self.key = key
        self.value = value

class IList(Instruction):
    stop = "stop"

    def __init__(self, context: str, *items: IItem):
        assert len(items) > 0, "Need at least one item in a List"
        self._context = context
        self._items = list(items)
    
    @override
    def describe(self) -> str:
        items = []
        for item in self._items:
            items.append(f"Write \"{wrap_text(item.key)}\"")
            if item.value is not None:
                items.append(item.value.describe())
        return self._context + enumerate_text(*items, add_scope=True)

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