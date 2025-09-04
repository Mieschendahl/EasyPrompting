from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from easy_prompting._utils import If, list_text, scope_text, wrap_text, extract_code

class ExtractionError(Exception):
    pass

class Instruction(ABC):
    stop = "stop"

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
            raise ExtractionError("Data extraction failed: extractor raised an error") from e

class ICode(IData):
    def __init__(self, text: str):
        super().__init__(text, extract_code)

class IItem(Instruction):
    def __init__(self, key: str, value: Optional[Instruction] = None, no_extract: bool = False):
        self.key = key
        self.value = value
        self.no_extract = no_extract
    
    def describe(self) -> str:
        return list_text(
            f"Write \"{wrap_text(self.key)}\"",
            None if self.value is None else self.value.describe()
        )
    
    def extract(self, data: str) -> Any:
        if self.value is None:
            return data
        return self.value.extract(data)        

class IList(Instruction):
    def __init__(self, *items: IItem, add_stop: bool = False):
        assert len(items) > 0, f"Need at least on item to describe a List"
        self.items = list(items)
        self.added_stop = add_stop
        
        if add_stop:
            self.items.append(IItem(Instruction.stop, no_extract=True))
    
    def describe(self) -> str:
        return "\n".join(item.describe() for item in self.items)

    def extract(self, data: str) -> list[Any]:
        extraction = []
        for item in self.items:
            key = wrap_text(item.key)
            if key not in data:
                raise ExtractionError(f"List extraction failed: missing key")
            head, data = data.split(key, 1)
            extraction.append(head)
        extraction = extraction[1:] + [data]
        
        extraction_out = []
        for i, item in enumerate(self.items):
            if not item.no_extract:
                extraction_out.append(item.extract(extraction[i]))
        return extraction_out
    
class IContainer(Instruction):
    def __init__(self, context: str, ilist: IList):
        self.context = context
        self.ilist = ilist
    
    def describe(self) -> str:
        return f"{self.context}{scope_text(self.ilist.describe())}"
    
    def extract(self, data: str) -> list[Any]:
        return self.ilist.extract(data)

class IRepetition(Instruction):
    def __init__(self, quantifier: str, *items: IItem):
        assert len(items) > 0, f"Need at least on item to describe a Repetition"
        self.quantifier = quantifier
        self.items = list(items)

    def describe(self) -> str:
        return f"{self.quantifier}{scope_text('\n'.join(item.describe() for item in self.items))}"

    def extract(self, data: str) -> list[list[Any]]:
        first_key = wrap_text(self.items[0].key)
        if first_key not in data:
            return []

        extractions = []
        while True:
            extraction = []
            for item in self.items:
                key = wrap_text(item.key)
                if key not in data:
                    raise ExtractionError(f"Repetition extraction failed: missing key")
                head, data = data.split(key, 1)
                extraction.append(head)
            extraction = extraction[1:] + [data]
            
            if first_key in extraction[-1]:
                extraction[-1], _ = data.split(first_key, 1)

            extraction_out = []
            for i, item in enumerate(self.items):
                if not item.no_extract:
                    extraction_out.append(item.extract(extraction[i]))
            
            extractions.append(extraction_out)
            if first_key not in data:
                return extractions

class IOption(Instruction):
    def __init__(self, condtion: str, ilist: IList):
        self.condition = condtion
        self.ilist = ilist
    
    def describe(self) -> str:
        return f"{self.condition}{scope_text(self.ilist.describe())}"
    
    def extract(self, data: str) -> list[Any]:
        return self.ilist.extract(data)

class IChoice(Instruction):
    def __init__(self, context: str, *options: IOption):
        self.context = context
        self.options = options

    def describe(self) -> str:
        return (
            self.context    
            +
            list_text(*[option.describe() for option in self.options], scope=True)
        )
    
    def extract(self, data) -> tuple[str, list[Any]]:
        for option in self.options:
            try:
                return option.ilist.items[0].key, option.extract(data)
            except ExtractionError as e:
                pass
        raise ExtractionError(f"Choice extraction failed: no valid choice")