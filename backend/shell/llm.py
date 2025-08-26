from abc import ABC, abstractmethod
from typing import Iterator, Tuple, TypeAlias

from .tools import T2SQLTools


class LLM(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def call_chat(self, messages: list, tools_handler: T2SQLTools | None) -> Iterator[str]:
        """
        Calls the LLM with the provided messages and returns an iterator over the response.
        """


class Element(ABC):
    @abstractmethod
    # Returns string or a tuple with field names and records
    def getcontent(self) -> str | Tuple[list[str], list[list[str]]]:
        """
        Converts the element to a dictionary representation.
        """


class TextElement(Element):
    def __init__(self, text: str):
        self.text: str = text

    def getcontent(self) -> str:
        return self.text


class GraphicsElement(Element):
    def __init__(self, image: str):
        self.image: str = image

    def getcontent(self) -> str:
        return self.image


class TableElement(Element):
    def __init__(self, data: list[dict[str, str]]):
        self.data: list[dict[str, str]] = data

    def get_content(self) -> Tuple[list[str], list[list[str]]]:
        if not self.data:
            return [], []
        fields = list(self.data[0].keys())
        records = [list(record.values()) for record in self.data]
        return fields, records


RecStrDictValue: TypeAlias = 'str | RecStrDict | list[RecStrDictValue]'
RecStrDict: TypeAlias = dict[str, RecStrDictValue]
History: TypeAlias = list[RecStrDict]
Result: TypeAlias = list[TextElement | GraphicsElement | TableElement]


class Shell(ABC):
    @abstractmethod
    def request(self, llm: LLM, tools: T2SQLTools, history: History, req: str) -> Tuple[Result, History]:
        """
        Processes the request using the LLM and tools, updating the history.
        Returns a tuple of Result and updated History.
        """
