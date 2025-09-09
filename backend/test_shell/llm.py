from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator, Tuple, TypeAlias

from t2sqltools.tools import T2SQLTools


class LLM(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def call_chat(self, messages: list, tools_handler: T2SQLTools | None) -> Iterator[str]:
        """
        Calls the LLM with the provided messages and returns an iterator over the response.
        """


@dataclass
class Element:
    pass


@dataclass
class TextElement(Element):
    """Carrier of literal texts. Anything that can possibly be found in an LLM reply will make it here: Markdown, links etc. so be prepared"""

    _content: str

    def __repr__(self) -> str:
        return f"TextElement(_content={self._content})"

    def getcontent(self) -> str:
        return self._content


@dataclass
class GraphicsElement(Element):
    """Carrier of a graphics element encoded as a legal string. For now this is PNG over base64"""

    _content: str

    def __repr__(self) -> str:
        return f"GraphicsElement(_content={self._content})"

    def getcontent(self) -> str:
        return self._content


@dataclass
class TableElement(Element):
    """Carrier of a table"""

    _content: list[dict[str, str]]

    def __repr__(self) -> str:
        return f"""TableElement(_content={self._content})"""

    def getcontent(self) -> list[dict[str, str]]:
        return self._content


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
