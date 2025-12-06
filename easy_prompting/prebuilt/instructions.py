from dataclasses import dataclass
from typing import Any, Callable, Optional, override

from easy_prompting.instruction import ExtractionError, Instruction
from easy_prompting.utils import enumerate_text, pad_text, scope_text, wrap_text
from easy_prompting.prebuilt.utils import extract_code, list_text

class DataI(Instruction):
    def __init__(self, text: str, extractor: Callable[[str], Any]):
        self._text = text
        self._extractor = extractor
    
    @override
    def describe(self) -> str:
        return self._text

    @override
    def extract(self, data: str) -> Any:
        try:
            return self._extractor(data)
        except Exception as e:
            raise ExtractionError(f"Data extraction failed: extractor {self._extractor} raised an error for {data!r}") from e

class TextI(DataI):
    @override
    def __init__(self, text: str):
        super().__init__(text, lambda x: x.strip())

class CodeI(DataI):
    @override
    def __init__(self, text: str, language: str = ""):
        super().__init__(text, extract_code)
        self._language = language

    @override
    def describe(self) -> str:
        return (
            f"Do the following"
            +
            enumerate_text(
                f"Write \"```{self._language}\\n\"",
                self._text,
                f"Write \"\\n```\"",
                add_scope=True
            )
        )

@dataclass
class Item:
    key: str
    value: Optional[Instruction] = None

class ListI(Instruction):
    stop = "stop"

    def __init__(self, context: str, *items: Item, add_stop: bool = False, effect: Optional[str] = None):
        assert len(items) > 0, "Need at least one item in a List"
        self._context = context
        self._items = list(items)
        self._add_stop = add_stop
        if self._add_stop:
            self._items.append(Item(ListI.stop))
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
        if self._add_stop:
            return extraction_out[:-1]
        return extraction_out
    
    @override
    def get_stop(self) -> Optional[str]:
        if self._add_stop:
            return wrap_text(ListI.stop)

class RepetitionI(Instruction):
    def __init__(self, quantifier: str, *items: Item):
        assert len(items) > 0, f"Need at least on item to describe a Repetition"
        self._quantifier = quantifier
        self._items = list(items)

    @override
    def describe(self) -> str:
        items = []
        for item in self._items:
            items.append(f"Write \"{wrap_text(item.key)}\"")
            if item.value is not None:
                items.append(item.value.describe())
        
        return self._quantifier + enumerate_text(*items, add_scope=True)

    @override
    def extract(self, data: str) -> Any:
        first_key = wrap_text(self._items[0].key)
        if first_key not in data:
            return []
        extractions = []
        while True:
            extraction = []
            for item in self._items:
                key = wrap_text(item.key)
                if key not in data:
                    raise ExtractionError(f"Repetition extraction failed: missing key {key!r} in {data!r}")
                head, data = data.split(key, 1)
                extraction.append(head)
            extraction = extraction[1:] + [data]
            if first_key in extraction[-1]:
                extraction[-1], _ = data.split(first_key, 1)
            extraction_out = []
            for i, item in enumerate(self._items):
                extraction_out.append(extraction[i] if item.value is None else item.value.extract(extraction[i]))
            extractions.append(extraction_out)
            if first_key not in data:
                return extractions

class ChoiceI(Instruction):
    def __init__(self, context: str, *options: ListI):
        self._context = context
        self._options = options

    @override
    def describe(self) -> str:
        return (
            self._context
            +
            list_text(*[option.describe() for option in self._options], add_scope=True)
        )

    @override
    def extract(self, data) -> tuple[str, Any]:
        _data = data
        keys = []
        for option in self._options:
            key = wrap_text(option._items[0].key)
            if key in data:
                return option._items[0].key, option.extract(data)
        keys = (wrap_text(option._items[0].key) for option in self._options)
        raise ExtractionError(f"Choice extraction failed: no valid key {keys} in {_data!r}")