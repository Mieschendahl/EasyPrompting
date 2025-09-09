from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from easy_prompting._utils import list_text, enumerate_text, wrap_text, extract_code

class ExtractionError(Exception):
    pass

class Instruction(ABC):
    @abstractmethod
    def describe(self) -> str:
        pass
    
    @abstractmethod
    def extract(self, data: str) -> Any:
        pass

class IData(Instruction):
    def __init__(self, text: str, extractor: Callable[[str], Any] = lambda x: x.strip()):
        self.text = text
        self.extractor = extractor
    
    def describe(self) -> str:
        return self.text

    def extract(self, data: str) -> Any:
        try:
            return self.extractor(data)
        except Exception as e:
            raise ExtractionError(f"Data extraction failed: extractor {self.extractor} raised an error for {data!r}") from e

class ICode(IData):
    def __init__(self, text: str):
        super().__init__(text, extract_code)

class IItem:
    def __init__(self, key: str, value: Optional[Instruction] = None):
        self.key = key
        self.value = value

class IList(Instruction):
    stop = "stop"

    def __init__(self, context: str, *items: IItem):
        assert len(items) > 0, "Need at least one item in a List"
        self.context = context
        self.items = list(items)
    
    def describe(self) -> str:
        items = []
        for item in self.items:
            items.append(f"Write \"{wrap_text(item.key)}\"")
            if item.value is not None:
                items.append(item.value.describe())
        
        return self.context + enumerate_text(*items, add_scope=True)

    def extract(self, data: str) -> list[Any]:
        extraction = []
        for item in self.items:
            key = wrap_text(item.key)
            if key not in data:
                raise ExtractionError(f"List extraction failed: missing key {key!r} in {data!r}")
            head, data = data.split(key, 1)
            extraction.append(head)
        extraction = extraction[1:] + [data]
        
        extraction_out = []
        for i, item in enumerate(self.items):
            extraction_out.append(extraction[i] if item.value is None else item.value.extract(extraction[i]))
        return extraction_out

class IRepetition(Instruction):
    def __init__(self, quantifier: str, *items: IItem):
        assert len(items) > 0, f"Need at least on item to describe a Repetition"
        self.quantifier = quantifier
        self.items = list(items)

    def describe(self) -> str:
        items = []
        for item in self.items:
            items.append(f"Write \"{wrap_text(item.key)}\"")
            if item.value is not None:
                items.append(item.value.describe())
        
        return self.quantifier + enumerate_text(*items, add_scope=True)

    def extract(self, data: str) -> Any:
        first_key = wrap_text(self.items[0].key)
        if first_key not in data:
            return []

        extractions = []
        while True:
            extraction = []
            for item in self.items:
                key = wrap_text(item.key)
                if key not in data:
                    raise ExtractionError(f"Repetition extraction failed: missing key {key!r} in {data!r}")
                head, data = data.split(key, 1)
                extraction.append(head)
            extraction = extraction[1:] + [data]
            
            if first_key in extraction[-1]:
                extraction[-1], _ = data.split(first_key, 1)

            extraction_out = []
            for i, item in enumerate(self.items):
                extraction_out.append(extraction[i] if item.value is None else item.value.extract(extraction[i]))

            extractions.append(extraction_out)
            if first_key not in data:
                return extractions

class IChoice(Instruction):
    def __init__(self, context: str, *options: IList):
        self.context = context
        self.options = options

    def describe(self) -> str:
        return (
            self.context
            +
            list_text(*[option.describe() for option in self.options], add_scope=True)
        )
    
    def extract(self, data) -> tuple[str, Any]:
        _data = data
        keys = []
        for option in self.options:
            key = wrap_text(option.items[0].key)
            if key in data:
                return option.items[0].key, option.extract(data)
        keys = (wrap_text(option.items[0].key) for option in self.options)
        raise ExtractionError(f"Choice extraction failed: no valid key {keys} in {_data!r}")